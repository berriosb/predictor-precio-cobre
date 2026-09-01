import type { Metadata } from "next";
import { DM_Mono, Manrope, Newsreader } from "next/font/google";
import "./globals.css";

const sans = Manrope({ subsets: ["latin"], variable: "--font-sans" });
const serif = Newsreader({ subsets: ["latin"], variable: "--font-serif" });
const mono = DM_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-mono" });

const SITE_URL = "https://predictor-precio-cobre.vercel.app";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Cobre / Forecast Lab",
    template: "%s · Cobre / Forecast Lab",
  },
  description:
    "Benchmark reproducible de forecasting 1-día sobre el precio del cobre (HG=F). Ridge frente a persistencia naïve con validación walk-forward 2020–2024.",
  applicationName: "Cobre / Forecast Lab",
  authors: [{ name: "Bastian Berrios", url: "https://github.com/berriosb" }],
  generator: "Next.js",
  keywords: [
    "cobre",
    "forecasting",
    "machine learning",
    "Ridge regression",
    "walk-forward validation",
    "Yahoo Finance",
    "HG=F",
    "benchmark",
    "data science",
    "time series",
  ],
  referrer: "origin-when-cross-origin",
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true },
  },
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "es_CL",
    url: "/",
    siteName: "Cobre / Forecast Lab",
    title: "Cobre / Forecast Lab — Predecir menos. Demostrar más.",
    description:
      "Quince años de precio diario del cobre (HG=F), evaluados con walk-forward. Ridge no supera consistentemente a la persistencia naïve.",
    images: [
      {
        url: "/og-image.svg",
        width: 1200,
        height: 630,
        alt: "Cobre / Forecast Lab — serie histórica HG=F y comparación Ridge vs naïve",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Cobre / Forecast Lab — Predecir menos. Demostrar más.",
    description:
      "Walk-forward honesto sobre 15 años de precio diario del cobre. Ridge vs naïve, 5 ventanas anuales.",
    images: ["/og-image.svg"],
    creator: "@berriosb",
  },
  icons: {
    icon: [{ url: "/icon.svg", type: "image/svg+xml" }],
    apple: [{ url: "/apple-icon.svg", type: "image/svg+xml" }],
  },
  other: {
    "theme-color": "#1e211f",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es-CL" className={`${sans.variable} ${serif.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
