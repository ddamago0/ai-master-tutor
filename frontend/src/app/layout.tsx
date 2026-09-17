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
      <body className="bg-black text-white antialiased selection:bg-coral selection:text-black min-h-screen">
        {children}
      </body>
    </html>
  );
}
