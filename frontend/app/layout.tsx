import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AIMedical — Platform AI Klinis',
  description: 'Platform AI medis dengan LangGraph, SIMRS MCP, dan Qdrant RAG.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
