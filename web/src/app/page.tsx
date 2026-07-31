import { Dashboard } from "@/components/Dashboard";
import data from "@/data/dashboard.json";
import type { DashboardData } from "@/lib/dashboard";

export default function Home() {
  return <Dashboard data={data as DashboardData} />;
}
