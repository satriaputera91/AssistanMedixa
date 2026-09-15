import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AssistantMedixa — Platform AI Klinis',
  description: 'Platform AI medis dengan LangGraph, SIMRS / Satu Sehat, dan Qdrant RAG.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
