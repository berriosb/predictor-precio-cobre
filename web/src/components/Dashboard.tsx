import { PriceChart } from "./PriceChart";
import { ValidationPanel } from "./ValidationPanel";
import type { DashboardData } from "@/lib/dashboard";

const nf = new Intl.NumberFormat("es-CL", { maximumFractionDigits: 3 });
const pct = new Intl.NumberFormat("es-CL", { maximumFractionDigits: 2 });

export function Dashboard({ data }: { data: DashboardData }) {
  return (
    <main>
      <div className="paper-grain" aria-hidden="true" />
      <div className="shell">
        <header className="topbar">
          <a className="brand" href="#overview"><strong>Cobre / Forecast Lab</strong><span>HG=F · Chile</span></a>
          <nav aria-label="Navegación principal">
            <a href="#overview">Visión</a><a href="#validation">Validación</a><a href="#method">Método</a>
            <a href="#data">Datos</a>
            <a className="github" href="https://github.com/berriosb/predictor-precio-cobre" target="_blank" rel="noreferrer">GitHub <span aria-hidden="true">↗</span></a>
          </nav>
        </header>

        <section className="intro" id="overview">
          <div>
            <p className="eyebrow">Caso de estudio · Forecasting 1 día</p>
            <h1>Predecir menos.<br/>Demostrar más.</h1>
            <p className="lede">
              Quince años de precio diario del cobre — <strong>4.137 cierres</strong> del futuro HG=F desde
              2010 — entrenados con <strong>29 variables</strong> (lags, rolling stats, calendario,
              volatilidad) y evaluados con validación walk-forward sobre cinco ventanas anuales.
            </p>
            <p className="lede lede-secondary">
              El resultado central no es un número espectacular: es descubrir que Ridge α 0,1{" "}
              <strong>no supera consistentemente a la persistencia naïve</strong>. Cuando el modelo no
              vence al “mañana será igual a hoy”, el valor del análisis está en decirlo, no en esconderlo.
            </p>
          </div>
          <aside className="intro-note">
            <span className="reading-mark">Lectura 04 min</span>
            <strong>Una lectura honesta del modelo</strong>
            <p>Un R² alto describe la persistencia de la serie. El valor del análisis está en medir cuánto agrega el modelo sobre el baseline más simple posible.</p>
            <ul className="intro-meta">
              <li><span>Datos</span><strong>Yahoo Finance HG=F</strong></li>
              <li><span>Modelo</span><strong>Ridge α 0,1 · scikit-learn</strong></li>
              <li><span>Framework</span><strong>Next.js 15 · React 19</strong></li>
            </ul>
          </aside>
        </section>

        <section className="metrics" aria-label="Métricas principales">
          <Metric label="Último cierre del dataset" value={`US$ ${nf.format(data.latest.price)}`} note={`por libra · ${formatDate(data.latest.date)}`} />
          <Metric label="R² walk-forward" value={nf.format(data.metrics.averageR2)} note={`promedio · ${data.walkForward.length} ventanas`} />
          <Metric label="MAPE promedio" value={`${pct.format(data.metrics.averageMape)}%`} note="2020—2024" />
          <Metric label="Ridge vs naïve" value={`${data.metrics.ridgeWins} / ${data.walkForward.length}`} note="ventanas donde Ridge gana" accent />
        </section>

        <PriceChart points={data.history} />

        <div className="story-grid" id="validation">
          <ValidationPanel rows={data.walkForward} />
          <aside className="panel truth">
            <span className="section-index">HALLAZGO PRINCIPAL</span>
            <div className="score">{data.metrics.naiveWins}/{data.walkForward.length}</div>
            <h2>El baseline naïve gana más veces.</h2>
            <p>
              Ridge mejora marginalmente en {yearsWhereRidgeWins(data)}. En las{" "}
              {data.walkForward.length - data.metrics.ridgeWins} ventanas restantes, copiar el cierre
              anterior obtiene menor error. La complejidad no siempre paga — y este benchmark lo
              documenta.
            </p>
            <blockquote>Un buen proyecto de datos no fuerza una victoria del modelo. Muestra cuándo la complejidad no paga.</blockquote>
          </aside>
        </div>

        <section className="method-section" id="method">
          <div className="section-title">
            <div>
              <span className="section-index">03 / MÉTODO</span>
              <h2>Cómo se construyó la evidencia</h2>
            </div>
            <p>El modelo respeta el orden temporal. Cada ventana usa solo información disponible hasta ese momento — nunca se entrena con datos del futuro.</p>
          </div>
          <div className="method">
            <Step index="01" code="DATA" title={`${nf.format(data.metrics.records)} cierres`} text="Serie diaria HG=F desde 2010. Datos ordenados, trazables y auditables. Descarga reproducible vía yfinance." />
            <Step index="02" code="FEATURES" title={`${data.metrics.features} variables`} text="Lags (1–30 días), rolling statistics 7/30/90, calendario, tendencia y volatilidad con shift(1) para evitar data leakage." />
            <Step index="03" code="MODEL" title={`Ridge α ${nf.format(data.metrics.alpha)}`} text="Regularización L2 para un espacio de features altamente correlacionadas. Sin normalización exótica, sin tuning agresivo." />
            <Step index="04" code="VALIDATION" title={`${data.walkForward.length} ventanas`} text="Reentrenamiento expansivo y evaluación anual 2020–2024. Misma métrica (MAE, RMSE, R², MAPE) en cada ventana." />
            <Step index="05" code="TRUTH TEST" title="Baseline naïve" text="La referencia mínima: el próximo cierre será igual al último. Si Ridge no lo vence, el análisis lo dice." />
          </div>
        </section>

        <section className="limits data-section" id="data">
          <div>
            <span className="section-index">04 / DATOS &amp; LÍMITES</span>
            <h2>El dataset detrás del benchmark</h2>
            <p className="data-blurb">
              Descargá la serie completa (4.137 cierres, USD/libra, formato CSV estándar) para
              reproducir el análisis, contrastar con tu propio modelo o explorar otras ventanas.
            </p>
            <a
              className="download-button"
              href="/cobre-hgf.csv"
              download
              aria-label="Descargar CSV con 4137 cierres diarios del cobre"
            >
              <span aria-hidden="true">↓</span> Descargar dataset completo (CSV, ~200KB)
            </a>
            <dl className="data-meta">
              <div><dt>Columnas</dt><dd>fecha, precio_cobre_usd_lb</dd></div>
              <div><dt>Rango</dt><dd>2010-05-13 → {data.latest.date}</dd></div>
              <div><dt>Fuente</dt><dd>Yahoo Finance · HG=F</dd></div>
              <div><dt>Licencia</dt><dd>MIT (repositorio)</dd></div>
            </dl>
          </div>
          <div className="limits-copy">
            <div>
              <h3>Lo que este modelo no promete</h3>
              <p>Forecast optimizado para un día bursátil. No anticipa shocks geopolíticos, no incorpora variables exógenas (tipo de cambio, inventarios LME, producción china) y no debe usarse como recomendación financiera.</p>
            </div>
            <div>
              <h3>Próximos pasos honestos</h3>
              <p>Horizontes multi-step quedan fuera hasta contar con targets directos y backtesting por horizonte. El siguiente paso razonable es comparar contra modelos con dependencias temporales explícitas (LSTM, Prophet) en el mismo régimen walk-forward.</p>
            </div>
          </div>
        </section>

        <footer>
          <div><strong>Cobre / Forecast Lab</strong><p>Benchmark reproducible de forecasting de corto plazo sobre el futuro continuo del cobre.</p></div>
          <div className="footer-meta">
            <span>Python · scikit-learn · Next.js</span>
            <span>Datos: Yahoo Finance HG=F</span>
            <span>Diseño y análisis: Bastian Berrios</span>
          </div>
        </footer>
      </div>
    </main>
  );
}

function Metric({ label, value, note, accent = false }: { label: string; value: string; note: string; accent?: boolean }) {
  return <article className="metric"><span>{label}</span><strong className={accent ? "accent" : ""}>{value}</strong><small>{note}</small></article>;
}

function Step({ index, code, title, text }: { index: string; code: string; title: string; text: string }) {
  return <article className="step"><span>{index} / {code}</span><h3>{title}</h3><p>{text}</p></article>;
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" }).format(new Date(`${date}T00:00:00Z`));
}

function yearsWhereRidgeWins(data: DashboardData): string {
  const wins = data.walkForward.filter((row) => row.ridgeMae < row.naiveMae).map((row) => row.year);
  if (wins.length === 0) return "ninguna ventana";
  if (wins.length === 1) return wins[0];
  if (wins.length === data.walkForward.length) return "todas las ventanas";
  const last = wins.pop();
  return `${wins.join(", ")} y ${last}`;
}
