import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MemoryVerse AI",
  description: "Your Personal Career Intelligence Engine.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
