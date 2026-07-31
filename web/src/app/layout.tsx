import type { Metadata } from "next";
import { DM_Mono, Manrope, Newsreader } from "next/font/google";
import "./globals.css";

const sans = Manrope({ subsets: ["latin"], variable: "--font-sans" });
const serif = Newsreader({ subsets: ["latin"], variable: "--font-serif" });
const mono = DM_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "Cobre / Forecast Lab",
  description: "Benchmark reproducible de forecasting del cobre: Ridge frente a persistencia naïve.",
  metadataBase: new URL("https://predictor-precio-cobre.vercel.app"),
  openGraph: {
    title: "Cobre / Forecast Lab",
    description: "Predecir menos. Demostrar más.",
    type: "website",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" className={`${sans.variable} ${serif.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
