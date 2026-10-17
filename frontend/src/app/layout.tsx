import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Compliance — AI Act & ISO/IEC 42001",
  description: "Plateforme intégrée de conformité IA : classification des risques AI Act et système de management ISO/IEC 42001.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="fr" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col font-sans">
        <header className="border-b border-slate-200 bg-white">
          <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
            <Link href="/" className="text-lg font-bold text-blue-900">
              AI Compliance <span className="hidden font-normal text-teal-700 sm:inline">· ISO 42001</span>
            </Link>
            <Link href="/diagnostic" className="rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800">
              Diagnostic gratuit
            </Link>
          </nav>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
          Hébergement souverain UE · Zero-Data Retention · Chiffrement AES-256 / TLS 1.3
        </footer>
      </body>
    </html>
  );
}
