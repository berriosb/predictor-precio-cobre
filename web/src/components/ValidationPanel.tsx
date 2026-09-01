"use client";

import { useState } from "react";
import type { ValidationRow } from "@/lib/dashboard";

type HelpProps = { open: boolean; onToggle: () => void; onClose: () => void };

function WalkForwardHelp({ open, onToggle, onClose }: HelpProps) {
  return (
    <div className={`help ${open ? "help-open" : ""}`}>
      <button
        type="button"
        className="help-trigger"
        aria-expanded={open}
        aria-controls="walk-forward-help"
        onClick={onToggle}
      >
        <span aria-hidden="true">?</span> ¿Qué es walk-forward?
      </button>
      {open ? (
        <div className="help-panel" id="walk-forward-help" role="region" aria-label="Explicación walk-forward">
          <button type="button" className="help-close" aria-label="Cerrar" onClick={onClose}>×</button>
          <p className="help-eyebrow">VALIDACIÓN TEMPORAL</p>
          <h3>Walk-forward honesto</h3>
          <p>
            En lugar de partir los datos una sola vez (train/test fijo), el modelo se reentrena cada año
            con <strong>toda la historia disponible hasta ese momento</strong> y se evalúa sobre los 12 meses
            siguientes. Esto simula el uso real: nunca se entrena con datos del futuro.
          </p>
          <ol>
            <li><strong>2020</strong> — entrena con 2010–2019, evalúa 2020.</li>
            <li><strong>2021</strong> — entrena con 2010–2020, evalúa 2021.</li>
            <li>… y así hasta 2024.</li>
          </ol>
          <p>
            El baseline naïve no se entrena: predice que el precio de mañana es igual al de hoy.
            Cuando Ridge no lo supera, <strong>la persistencia del cobre ya es una predicción fuerte</strong>.
          </p>
        </div>
      ) : null}
    </div>
  );
}

function YearDetail({ row }: { row: ValidationRow }) {
  const ridgeWins = row.ridgeMae < row.naiveMae;
  const delta = ((row.naiveMae - row.ridgeMae) / row.naiveMae) * 100;
  return (
    <div className="year-detail" aria-live="polite">
      <div className="year-detail-head">
        <span className="section-index">VENTANA {row.year}</span>
        <h3>
          {row.testStart} <span aria-hidden="true">→</span> {row.testEnd}
        </h3>
      </div>
      <dl className="year-grid">
        <div><dt>Train</dt><dd>{row.trainRows.toLocaleString("es-CL")} filas</dd></div>
        <div><dt>Test</dt><dd>{row.testRows.toLocaleString("es-CL")} filas</dd></div>
        <div><dt>Ridge MAE</dt><dd>US$ {row.ridgeMae.toFixed(4)}</dd></div>
        <div><dt>Naïve MAE</dt><dd>US$ {row.naiveMae.toFixed(4)}</dd></div>
        <div><dt>R²</dt><dd>{row.r2.toFixed(4)}</dd></div>
        <div><dt>MAPE</dt><dd>{row.mape.toFixed(2)}%</dd></div>
      </dl>
      <p className={`year-verdict ${ridgeWins ? "ridge-win" : "naive-win"}`}>
        {ridgeWins ? "Ridge" : "Naïve"} gana por{" "}
        <strong>{Math.abs(delta).toFixed(2)}%</strong>{" "}
        de MAE ({ridgeWins ? "menor error" : "menor error"} del modelo vs baseline).
      </p>
    </div>
  );
}

export function ValidationPanel({ rows }: { rows: ValidationRow[] }) {
  const maxMae = Math.max(...rows.flatMap((row) => [row.ridgeMae, row.naiveMae])) * 1.08;
  const [helpOpen, setHelpOpen] = useState(false);
  const [activeYear, setActiveYear] = useState<string>(rows.at(-1)?.year ?? rows[0].year);
  const active = rows.find((row) => row.year === activeYear) ?? rows[0];

  return (
    <section className="panel validation-panel" aria-labelledby="validation-title">
      <div className="panel-head">
        <div>
          <span className="section-index">02 / VALIDACIÓN</span>
          <h2 id="validation-title">El modelo frente a lo obvio</h2>
          <p>MAE por ventana · menor es mejor</p>
        </div>
        <div className="panel-head-actions">
          <WalkForwardHelp
            open={helpOpen}
            onToggle={() => setHelpOpen((value) => !value)}
            onClose={() => setHelpOpen(false)}
          />
          <span className="status">Walk-forward verificado</span>
        </div>
      </div>
      <div className="bar-area">
        {rows.map((row) => {
          const ridgeWins = row.ridgeMae < row.naiveMae;
          const isActive = row.year === activeYear;
          return (
            <button
              type="button"
              className={`bar-row bar-row-button ${isActive ? "active" : ""}`}
              key={row.year}
              onClick={() => setActiveYear(row.year)}
              aria-pressed={isActive}
              aria-label={`Ver detalle de ${row.year}`}
            >
              <span className="bar-year">{row.year}</span>
              <div className="bars" aria-label={`${row.year}: Ridge ${row.ridgeMae}, naïve ${row.naiveMae}`}>
                <span className="bar ridge" style={{ width: `${(row.ridgeMae / maxMae) * 100}%` }} />
                <span className="bar naive" style={{ width: `${(row.naiveMae / maxMae) * 100}%` }} />
              </div>
              <span className={`winner ${ridgeWins ? "ridge-win" : "naive-win"}`}>{ridgeWins ? "Ridge" : "Naïve"}</span>
            </button>
          );
        })}
        <div className="bar-key"><span><i className="key-ridge" />Ridge</span><span><i className="key-naive" />Naïve · cierre anterior</span></div>
      </div>
      <YearDetail row={active} />
    </section>
  );
}
