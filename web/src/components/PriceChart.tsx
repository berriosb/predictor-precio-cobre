"use client";

import { useMemo, useState } from "react";
import { extent, filterHistory, linePath, type PricePoint, type RangeKey } from "@/lib/dashboard";

const WIDTH = 1200;
const HEIGHT = 360;
const PAD = { left: 56, right: 20, top: 24, bottom: 36 };
const ranges: { key: RangeKey; label: string }[] = [
  { key: "2Y", label: "2A" },
  { key: "5Y", label: "5A" },
  { key: "10Y", label: "10A" },
  { key: "ALL", label: "Todo" },
];

export function PriceChart({ points }: { points: PricePoint[] }) {
  const [range, setRange] = useState<RangeKey>("ALL");
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const visible = useMemo(() => filterHistory(points, range), [points, range]);
  const [min, max] = extent(visible.map((point) => point.price));
  const path = linePath(visible, WIDTH, HEIGHT, PAD);
  const x = (index: number) => PAD.left + (index / Math.max(visible.length - 1, 1)) * (WIDTH - PAD.left - PAD.right);
  const y = (value: number) => PAD.top + ((max - value) / (max - min)) * (HEIGHT - PAD.top - PAD.bottom);
  const ticks = Array.from({ length: 5 }, (_, index) => min + ((max - min) * index) / 4);
  const yearStep = Math.max(1, Math.floor(visible.length / 6));
  const active = activeIndex === null ? null : visible[activeIndex];

  function pointerIndex(clientX: number, rect: DOMRect) {
    const svgX = ((clientX - rect.left) / rect.width) * WIDTH;
    const ratio = (svgX - PAD.left) / (WIDTH - PAD.left - PAD.right);
    return Math.max(0, Math.min(visible.length - 1, Math.round(ratio * (visible.length - 1))));
  }

  return (
    <section className="panel price-panel" aria-labelledby="price-title">
      <div className="panel-head">
        <div>
          <span className="section-index">01 / SERIE</span>
          <h2 id="price-title">Precio histórico del cobre</h2>
          <p>Futuros HG=F · USD por libra · datos Yahoo Finance</p>
        </div>
        <div className="range" aria-label="Rango de tiempo">
          {ranges.map((item) => (
            <button
              type="button"
              key={item.key}
              className={range === item.key ? "active" : ""}
              aria-pressed={range === item.key}
              onClick={() => { setRange(item.key); setActiveIndex(null); }}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
      <div className="chart-wrap">
        {active && activeIndex !== null ? (
          <div className="chart-tooltip" style={{ left: `${(x(activeIndex) / WIDTH) * 100}%`, top: `${(y(active.price) / HEIGHT) * 100}%` }}>
            <strong>US$ {active.price.toFixed(3)}</strong><span>{active.date}</span>
          </div>
        ) : null}
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="Serie histórica interactiva del precio del cobre desde 2010">
          <defs>
            <linearGradient id="copper-area" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--copper)" stopOpacity="0.12" />
              <stop offset="100%" stopColor="var(--copper)" stopOpacity="0" />
            </linearGradient>
          </defs>
          {ticks.map((tick) => (
            <g key={tick}>
              <line x1={PAD.left} y1={y(tick)} x2={WIDTH - PAD.right} y2={y(tick)} className="grid-line" />
              <text x={PAD.left - 12} y={y(tick) + 4} textAnchor="end" className="axis-label">{tick.toFixed(1)}</text>
            </g>
          ))}
          {visible.map((point, index) => index % yearStep === 0 ? (
            <text key={`${point.date}-label`} x={x(index)} y={HEIGHT - 10} textAnchor="middle" className="axis-label">{point.date.slice(0, 4)}</text>
          ) : null)}
          {[["2020-03-01", "COVID-19"], ["2022-02-24", "Ucrania"]].map(([date, label]) => {
            const index = visible.findIndex((point) => point.date >= date);
            return index > 0 ? <g key={date}><line x1={x(index)} y1={PAD.top} x2={x(index)} y2={HEIGHT - PAD.bottom} className="event-line"/><text x={x(index) + 6} y={PAD.top + 14} className="event-label">{label}</text></g> : null;
          })}
          <path d={`${path} L${WIDTH - PAD.right},${HEIGHT - PAD.bottom} L${PAD.left},${HEIGHT - PAD.bottom} Z`} fill="url(#copper-area)" />
          <path d={path} className="price-line" />
          {active && activeIndex !== null ? <><line x1={x(activeIndex)} y1={PAD.top} x2={x(activeIndex)} y2={HEIGHT - PAD.bottom} className="cursor-line"/><circle cx={x(activeIndex)} cy={y(active.price)} r="4" className="cursor-point"/></> : null}
          <rect
            x={PAD.left} y={PAD.top} width={WIDTH - PAD.left - PAD.right} height={HEIGHT - PAD.top - PAD.bottom}
            fill="transparent" tabIndex={0}
            onPointerMove={(event) => setActiveIndex(pointerIndex(event.clientX, event.currentTarget.getBoundingClientRect()))}
            onPointerLeave={() => setActiveIndex(null)}
            onKeyDown={(event) => {
              if (event.key === "ArrowRight") setActiveIndex((index) => Math.min((index ?? -1) + 1, visible.length - 1));
              if (event.key === "ArrowLeft") setActiveIndex((index) => Math.max((index ?? visible.length) - 1, 0));
            }}
          />
        </svg>
      </div>
      <div className="chart-foot"><span><i className="legend-price"/>Precio de cierre</span><span className="mono">Eventos anotados: COVID-19 · Guerra en Ucrania</span></div>
    </section>
  );
}
