export type PricePoint = { date: string; price: number };
export type ValidationRow = {
  year: string;
  ridgeMae: number;
  naiveMae: number;
  r2: number;
  mape: number;
};
export type DashboardData = {
  generatedFrom: Record<string, string>;
  latest: PricePoint;
  history: PricePoint[];
  walkForward: ValidationRow[];
  metrics: {
    averageR2: number;
    averageMape: number;
    ridgeWins: number;
    naiveWins: number;
    features: number;
    records: number;
    alpha: number;
  };
};

export type RangeKey = "2Y" | "5Y" | "10Y" | "ALL";

export function filterHistory(points: PricePoint[], range: RangeKey): PricePoint[] {
  if (range === "ALL" || points.length === 0) return points;
  const years = Number.parseInt(range, 10);
  const maxDate = new Date(`${points.at(-1)?.date}T00:00:00Z`);
  maxDate.setUTCFullYear(maxDate.getUTCFullYear() - years);
  return points.filter((point) => new Date(`${point.date}T00:00:00Z`) >= maxDate);
}

export function extent(values: number[], padding = 0.08): [number, number] {
  if (values.length === 0) return [0, 1];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || Math.max(Math.abs(max), 1);
  return [min - span * padding, max + span * padding];
}

export function summary(rows: ValidationRow[]) {
  const ridgeWins = rows.filter((row) => row.ridgeMae < row.naiveMae).length;
  return {
    ridgeWins,
    naiveWins: rows.length - ridgeWins,
    averageR2: rows.reduce((sum, row) => sum + row.r2, 0) / rows.length,
    averageMape: rows.reduce((sum, row) => sum + row.mape, 0) / rows.length,
  };
}

export function linePath(
  points: PricePoint[],
  width: number,
  height: number,
  padding = { left: 56, right: 20, top: 24, bottom: 36 },
): string {
  if (points.length < 2) return "";
  const [min, max] = extent(points.map((point) => point.price));
  const x = (index: number) => padding.left + (index / (points.length - 1)) * (width - padding.left - padding.right);
  const y = (value: number) => padding.top + ((max - value) / (max - min)) * (height - padding.top - padding.bottom);
  return points.map((point, index) => `${index === 0 ? "M" : "L"}${x(index).toFixed(2)},${y(point.price).toFixed(2)}`).join(" ");
}
