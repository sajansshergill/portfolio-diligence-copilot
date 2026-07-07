import "./globals.css";

export const metadata = {
  title: "Portfolio Diligence Copilot",
  description: "AI-native diligence and portfolio monitoring workbench",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
