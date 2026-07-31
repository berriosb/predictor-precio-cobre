import { PriceChart } from "./PriceChart";
import type { DashboardData } from "@/lib/dashboard";

const nf = new Intl.NumberFormat("es-CL", { maximumFractionDigits: 3 });

export function Dashboard({ data }: { data: DashboardData }) {
  const maxMae = Math.max(...data.walkForward.flatMap((row) => [row.ridgeMae, row.naiveMae])) * 1.08;
  return (
    <main>
      <div className="paper-grain" aria-hidden="true" />
      <div className="shell">
        <header className="topbar">
          <a className="brand" href="#overview"><strong>Cobre / Forecast Lab</strong><span>HG=F · Chile</span></a>
          <nav aria-label="Navegación principal">
            <a href="#overview">Visión</a><a href="#validation">Validación</a><a href="#method">Método</a>
            <a className="github" href="https://github.com/berriosb/predictor-precio-cobre" target="_blank" rel="noreferrer">GitHub <span aria-hidden="true">↗</span></a>
          </nav>
        </header>

        <section className="intro" id="overview">
          <div>
            <p className="eyebrow">Caso de estudio · Forecasting 1 día</p>
            <h1>Predecir menos.<br/>Demostrar más.</h1>
            <p className="lede">Quince años de precio diario del cobre, evaluados con validación walk-forward. El resultado central no es un número espectacular: es descubrir que Ridge no supera consistentemente a una persistencia naïve.</p>
          </div>
          <aside className="intro-note"><span className="reading-mark">Lectura 04 min</span><strong>Una lectura honesta del modelo</strong><p>Un R² alto describe la persistencia de la serie. El valor del análisis está en medir cuánto agrega el modelo sobre “mañana será igual a hoy”.</p></aside>
        </section>

        <section className="metrics" aria-label="Métricas principales">
          <Metric label="Último cierre del dataset" value={`US$ ${nf.format(data.latest.price)}`} note={`por libra · ${formatDate(data.latest.date)}`} />
          <Metric label="R² walk-forward" value={nf.format(data.metrics.averageR2)} note="promedio · 5 ventanas" />
          <Metric label="MAPE promedio" value={`${nf.format(data.metrics.averageMape)}%`} note="2020—2024" />
          <Metric label="Ridge vs naïve" value={`${data.metrics.ridgeWins} / 5`} note="ventanas donde Ridge gana" accent />
        </section>

        <PriceChart points={data.history} />

        <div className="story-grid" id="validation">
          <section className="panel validation-panel" aria-labelledby="validation-title">
            <div className="panel-head"><div><span className="section-index">02 / VALIDACIÓN</span><h2 id="validation-title">El modelo frente a lo obvio</h2><p>MAE por ventana · menor es mejor</p></div><span className="status">Walk-forward verificado</span></div>
            <div className="bar-area">
              {data.walkForward.map((row) => {
                const ridgeWins = row.ridgeMae < row.naiveMae;
                return <div className="bar-row" key={row.year}>
                  <span className="bar-year">{row.year}</span>
                  <div className="bars" aria-label={`${row.year}: Ridge ${row.ridgeMae}, naïve ${row.naiveMae}`}>
                    <span className="bar ridge" style={{ width: `${(row.ridgeMae / maxMae) * 100}%` }} />
                    <span className="bar naive" style={{ width: `${(row.naiveMae / maxMae) * 100}%` }} />
                  </div>
                  <span className={`winner ${ridgeWins ? "ridge-win" : "naive-win"}`}>{ridgeWins ? "Ridge" : "Naïve"}</span>
                </div>;
              })}
              <div className="bar-key"><span><i className="key-ridge"/>Ridge</span><span><i className="key-naive"/>Naïve · cierre anterior</span></div>
            </div>
          </section>
          <aside className="panel truth"><span className="section-index">HALLAZGO PRINCIPAL</span><div className="score">{data.metrics.naiveWins}/5</div><h2>El baseline naïve gana más veces.</h2><p>Ridge mejora marginalmente en 2021 y 2023. En las otras tres ventanas, copiar el precio anterior obtiene menor error.</p><blockquote>Un buen proyecto de datos no fuerza una victoria del modelo. Muestra cuándo la complejidad no paga.</blockquote></aside>
        </div>

        <section className="method-section" id="method">
          <div className="section-title"><div><span className="section-index">03 / MÉTODO</span><h2>Cómo se construyó la evidencia</h2></div><p>El modelo respeta el orden temporal. Cada ventana usa solo información disponible hasta ese momento.</p></div>
          <div className="method">
            <Step index="01" code="DATA" title={`${nf.format(data.metrics.records)} cierres`} text="Serie diaria HG=F desde 2010. Datos ordenados, trazables y auditables." />
            <Step index="02" code="FEATURES" title={`${data.metrics.features} variables`} text="Lags, rolling statistics, calendario, tendencia y volatilidad con shift(1)." />
            <Step index="03" code="MODEL" title={`Ridge α ${nf.format(data.metrics.alpha)}`} text="Regularización para un espacio de features altamente correlacionado." />
            <Step index="04" code="VALIDATION" title="5 ventanas" text="Reentrenamiento expansivo y evaluación anual de 2020 a 2024." />
            <Step index="05" code="TRUTH TEST" title="Baseline naïve" text="La referencia mínima: el próximo cierre será igual al último." />
          </div>
        </section>

        <section className="limits" aria-labelledby="limits-title">
          <div><span className="section-index">04 / LÍMITES</span><h2 id="limits-title">Lo que este modelo no promete</h2></div>
          <div className="limits-copy"><p>Forecast optimizado para un día bursátil. No anticipa shocks geopolíticos, no incorpora variables exógenas y no debe usarse como recomendación financiera.</p><p>Los horizontes multi-step quedan fuera hasta contar con targets directos y backtesting por horizonte.</p></div>
        </section>

        <footer><div><strong>Cobre / Forecast Lab</strong><p>Benchmark reproducible de forecasting de corto plazo.</p></div><div className="footer-meta"><span>Python · scikit-learn · Next.js</span><span>Datos: Yahoo Finance HG=F</span><span>Diseño y análisis: Bastian Berrios</span></div></footer>
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
