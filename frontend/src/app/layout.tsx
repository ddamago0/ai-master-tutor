import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Master Tutor",
  description: "High-performance proactive AI tutoring with Active Recall & Spaced Repetition",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="dark">
      <body className="bg-neutral-950 text-neutral-100 antialiased selection:bg-neutral-800 selection:text-neutral-50 min-h-screen">
        {children}
      </body>
    </html>
  );
}
