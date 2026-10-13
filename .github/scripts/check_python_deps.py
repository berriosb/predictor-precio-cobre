#!/usr/bin/env python3
"""Verifica que todo import de terceros del pipeline este en requirements.txt.

Heuristica simple, sin instalar dependencias:

- Parsea imports de src/ y app.py con ast.
- Descarta stdlib y modulos locales (src, app, config).
- Un modulo NO debe exigirse si el unico sitio donde se importa esta dentro
  de un try/except ImportError, porque el codigo degrada con mensaje accionable.
  Esos se listan como opcionales para que la revision los vea.
- Para el resto, exige que el nombre del paquete aparezca en requirements.txt.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = ROOT / "requirements.txt"
TARGETS = [*sorted((ROOT / "src").rglob("*.py")), ROOT / "app.py"]

# Nombre del modulo importado -> nombre del paquete en requirements.txt
IMPORT_TO_PACKAGE = {
    "sklearn": "scikit-learn",
    "yaml": "pyyaml",
    "cv2": "opencv-python",
}

# Guardados con try/except ImportError: el pipeline no los necesita.
KNOWN_OPTIONAL = {"xgboost", "pmdarima"}


def imported_modules(tree: ast.Module) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                found.add(node.module.split(".")[0])
    return found


def guarded_imports(tree: ast.Module) -> set[str]:
    """Modulos importados dentro de un try/except ImportError."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        catches_import_error = any(
            (isinstance(h.type, ast.Name) and h.type.id == "ImportError")
            or (isinstance(h.type, ast.Tuple) and any(
                isinstance(e, ast.Name) and e.id == "ImportError" for e in h.type.elts
            ))
            for h in node.handlers
        )
        if not catches_import_error:
            continue
        for stmt in node.body:
            found |= imported_modules(ast.Module(body=[stmt], type_ignores=[]))
    return found


def declared_packages() -> set[str]:
    """Paquetes realmente declarados en requirements.txt (ignora comentarios).

    Buscar el nombre en el archivo crudo daria falsos negativos: el header
    menciona statsmodels y pmdarima al explicar que faltaban, y un simple
    'in' lo daria por declarado.
    """
    names: set[str] = set()
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        match = re.match(r"^([A-Za-z0-9._-]+)", line)
        if match:
            names.add(match.group(1).lower())
    return names


def main() -> int:
    stdlib = set(sys.stdlib_module_names)
    local = {"src", "app", "config", "predictor"}

    required: set[str] = set()
    guarded_only: set[str] = set()

    for path in TARGETS:
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        guarded = guarded_imports(tree)
        for module in imported_modules(tree):
            if module in stdlib or module in local:
                continue
            if module in KNOWN_OPTIONAL:
                continue
            if module in guarded:
                guarded_only.add(module)
            else:
                required.add(module)

    # Si se importa sin guard en algun sitio, es requerido aunque en otro
    # punto de entrada esté protegido con try/except.
    optional = guarded_only - required

    declared = declared_packages()
    missing = sorted(
        m for m in required if IMPORT_TO_PACKAGE.get(m, m).lower() not in declared
    )

    print(f"Requeridos: {', '.join(sorted(required)) or '(ninguno)'}")
    print(f"Opcionales (try/except): {', '.join(sorted(optional)) or '(ninguno)'}")

    if missing:
        print("\nFALTAN en requirements.txt:", file=sys.stderr)
        for module in missing:
            print(f"  - {module} (paquete: {IMPORT_TO_PACKAGE.get(module, module)})", file=sys.stderr)
        return 1

    print("\nOK: todos los imports de terceros requeridos estan declarados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())