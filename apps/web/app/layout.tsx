import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "PRO EDGE · Sports Intelligence",
  description:
    "Transparent NFL and NBA sports research. Offline demo foundation.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
