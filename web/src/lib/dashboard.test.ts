import { describe, expect, it } from "vitest";
import { extent, filterHistory, linePath, summary, type PricePoint, type ValidationRow } from "./dashboard";

const points: PricePoint[] = [
  { date: "2020-01-01", price: 2 },
  { date: "2023-01-01", price: 4 },
  { date: "2024-01-01", price: 6 },
];

const rows: ValidationRow[] = [
  { year: "2023", ridgeMae: 0.03, naiveMae: 0.04, r2: 0.9, mape: 1 },
  { year: "2024", ridgeMae: 0.05, naiveMae: 0.04, r2: 0.8, mape: 2 },
];

describe("dashboard helpers", () => {
  it("filters history relative to the last available point", () => {
    expect(filterHistory(points, "2Y")).toEqual(points.slice(1));
    expect(filterHistory(points, "ALL")).toEqual(points);
  });

  it("returns a padded numeric extent", () => {
    expect(extent([2, 6])).toEqual([1.68, 6.32]);
  });

  it("summarizes wins and average metrics", () => {
    const result = summary(rows);
    expect(result.ridgeWins).toBe(1);
    expect(result.naiveWins).toBe(1);
    expect(result.averageR2).toBeCloseTo(0.85);
    expect(result.averageMape).toBeCloseTo(1.5);
  });

  it("builds a finite SVG path", () => {
    const path = linePath(points, 1000, 300);
    expect(path.startsWith("M")).toBe(true);
    expect(path).not.toContain("NaN");
    expect(path.split("L")).toHaveLength(3);
  });
});
