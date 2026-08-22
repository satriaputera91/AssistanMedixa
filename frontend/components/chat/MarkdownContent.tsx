'use client';

import React from 'react';

interface MarkdownContentProps {
  content: string;
}

/**
 * Format markdown text inline: bold (**text**), code (`code`), italic (*text*).
 */
function renderInline(text: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    // Bold: **text**
    const boldMatch = remaining.match(/^([\s\S]*?)\*\*([\s\S]+?)\*\*([\s\S]*)/);
    // Inline code: `text`
    const codeMatch = remaining.match(/^([\s\S]*?)`([^`]+)`([\s\S]*)/);

    if (boldMatch && (!codeMatch || boldMatch[1].length <= codeMatch[1].length)) {
      if (boldMatch[1]) parts.push(<span key={key++}>{boldMatch[1]}</span>);
      parts.push(
        <strong key={key++} className="font-bold text-emerald-950 dark:text-emerald-300">
          {boldMatch[2]}
        </strong>
      );
      remaining = boldMatch[3];
      continue;
    }

    if (codeMatch) {
      if (codeMatch[1]) parts.push(<span key={key++}>{codeMatch[1]}</span>);
      parts.push(
        <code
          key={key++}
          className="px-1.5 py-0.5 rounded bg-emerald-100/80 dark:bg-slate-800 text-emerald-900 dark:text-emerald-300 font-mono text-[11px] border border-emerald-200 dark:border-slate-700"
        >
          {codeMatch[2]}
        </code>
      );
      remaining = codeMatch[3];
      continue;
    }

    // No matches, push the rest
    parts.push(<span key={key++}>{remaining}</span>);
    break;
  }

  return <>{parts}</>;
}

function isDisclaimer(text: string): boolean {
  const lower = text.toLowerCase();
  return (
    lower.includes('disclaimer') ||
    lower.includes('clinical disclaimer') ||
    lower.includes('keputusan klinis') ||
    lower.includes('bukan pengganti diagnosis') ||
    lower.includes('ai decision support tool') ||
    lower.includes('divalidasi oleh tenaga medis') ||
    lower.startsWith('*(⚠️') ||
    lower.startsWith('*⚠️') ||
    lower.startsWith('⚠️')
  );
}

function cleanDisclaimer(text: string): string {
  return text
    .replace(/^\*\(?\s*/, '')
    .replace(/\)?\*\s*$/, '')
    .replace(/^⚠️\s*/, '')
    .trim();
}

export default function MarkdownContent({ content }: MarkdownContentProps) {
  if (!content) return null;

  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];

  let i = 0;
  let elemKey = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // Empty line
    if (!trimmed) {
      i++;
      continue;
    }

    // Special Disclaimer Box (Small yellow text in amber box)
    if (isDisclaimer(trimmed)) {
      elements.push(
        <div
          key={elemKey++}
          className="my-3 p-2.5 rounded-xl border border-amber-300 dark:border-amber-500/40 bg-amber-50/90 dark:bg-amber-950/40 text-[10px] sm:text-[11px] leading-relaxed text-amber-800 dark:text-amber-300 flex items-start gap-2 shadow-xs"
        >
          <span className="text-sm shrink-0 leading-none mt-0.5">⚠️</span>
          <div className="flex-1 font-medium text-amber-900 dark:text-amber-300">
            {renderInline(cleanDisclaimer(trimmed))}
          </div>
        </div>
      );
      i++;
      continue;
    }

    // Headings
    if (trimmed.startsWith('### ')) {
      elements.push(
        <h4 key={elemKey++} className="text-sm font-bold text-emerald-900 dark:text-emerald-300 mt-3.5 mb-1.5 uppercase tracking-wide">
          {renderInline(trimmed.replace(/^###\s+/, ''))}
        </h4>
      );
      i++;
      continue;
    }

    if (trimmed.startsWith('## ')) {
      elements.push(
        <h3
          key={elemKey++}
          className="text-base font-bold text-emerald-950 dark:text-white mt-4 mb-2 pb-1 border-b border-emerald-200/60 dark:border-slate-800 flex items-center gap-1.5"
        >
          <span className="w-1.5 h-4 bg-emerald-500 rounded-sm inline-block" />
          {renderInline(trimmed.replace(/^##\s+/, ''))}
        </h3>
      );
      i++;
      continue;
    }

    if (trimmed.startsWith('# ')) {
      elements.push(
        <h2 key={elemKey++} className="text-lg font-black text-emerald-950 dark:text-white mt-5 mb-2.5">
          {renderInline(trimmed.replace(/^#\s+/, ''))}
        </h2>
      );
      i++;
      continue;
    }

    // Horizontal Rule
    if (/^---$|^___$|^\*\*\*$/.test(trimmed)) {
      elements.push(<hr key={elemKey++} className="my-3 border-emerald-200 dark:border-slate-800" />);
      i++;
      continue;
    }

    // Blockquote
    if (trimmed.startsWith('> ')) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('> ')) {
        quoteLines.push(lines[i].trim().replace(/^>\s*/, ''));
        i++;
      }
      elements.push(
        <div
          key={elemKey++}
          className="my-2 border-l-2 border-emerald-500 pl-3 py-1.5 bg-emerald-50/60 dark:bg-slate-800/60 rounded-r text-[13px] text-emerald-800 dark:text-slate-300 italic"
        >
          {quoteLines.map((ql, qIdx) => (
            <p key={qIdx}>{renderInline(ql)}</p>
          ))}
        </div>
      );
      continue;
    }

    // Bullet List (*, -, +)
    if (/^[\*\-\+]\s+/.test(trimmed)) {
      const listItems: string[] = [];
      while (i < lines.length && /^[\*\-\+]\s+/.test(lines[i].trim())) {
        listItems.push(lines[i].trim().replace(/^[\*\-\+]\s+/, ''));
        i++;
      }
      elements.push(
        <ul key={elemKey++} className="my-2 space-y-1.5 pl-4 list-disc marker:text-emerald-500 text-[13.5px] sm:text-[14px] text-emerald-950 dark:text-slate-100">
          {listItems.map((item, idx) => (
            <li key={idx} className="leading-relaxed">
              {renderInline(item)}
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // Numbered List
    if (/^\d+\.\s+/.test(trimmed)) {
      const numItems: string[] = [];
      while (i < lines.length && /^\d+\.\s+/.test(lines[i].trim())) {
        numItems.push(lines[i].trim().replace(/^\d+\.\s+/, ''));
        i++;
      }
      elements.push(
        <ol key={elemKey++} className="my-2 space-y-1.5 pl-4 list-decimal marker:text-emerald-600 dark:marker:text-emerald-400 text-[13.5px] sm:text-[14px] text-emerald-950 dark:text-slate-100">
          {numItems.map((item, idx) => (
            <li key={idx} className="leading-relaxed">
              {renderInline(item)}
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // Markdown Table (| Col 1 | Col 2 |)
    if (trimmed.startsWith('|') && trimmed.endsWith('|') && i + 1 < lines.length && /^\|[\s\-:|]+\|$/.test(lines[i + 1].trim())) {
      const headerRow = trimmed;
      const separatorRow = lines[i + 1].trim();
      const headers = headerRow
        .split('|')
        .slice(1, -1)
        .map((h) => h.trim());

      i += 2; // skip header and separator
      const dataRows: string[][] = [];

      while (i < lines.length && lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|')) {
        const rowCells = lines[i]
          .trim()
          .split('|')
          .slice(1, -1)
          .map((c) => c.trim());
        dataRows.push(rowCells);
        i++;
      }

      elements.push(
        <div
          key={elemKey++}
          className="my-3.5 overflow-x-auto rounded-2xl border border-emerald-200 dark:border-slate-800 shadow-xs bg-white dark:bg-slate-900/90"
        >
          <table className="w-full text-left text-xs sm:text-[13px] border-collapse min-w-[340px]">
            <thead>
              <tr className="bg-emerald-100/70 dark:bg-slate-800 border-b border-emerald-200 dark:border-slate-700 text-emerald-950 dark:text-emerald-300 font-bold uppercase text-[11px] tracking-wider">
                {headers.map((h, hIdx) => (
                  <th key={hIdx} className="px-4 py-2.5 font-bold">
                    {renderInline(h)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-emerald-100 dark:divide-slate-800/80">
              {dataRows.map((row, rIdx) => (
                <tr
                  key={rIdx}
                  className="hover:bg-emerald-50/60 dark:hover:bg-slate-800/50 transition-colors odd:bg-transparent even:bg-emerald-50/20 dark:even:bg-slate-900/40"
                >
                  {row.map((cell, cIdx) => (
                    <td key={cIdx} className="px-4 py-2.5 text-emerald-900 dark:text-slate-200 leading-snug">
                      {renderInline(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    // Code block (```)
    if (trimmed.startsWith('```')) {
      const codeLines: string[] = [];
      i++; // skip opening ```
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      if (i < lines.length) i++; // skip closing ```
      elements.push(
        <pre
          key={elemKey++}
          className="my-2.5 p-3.5 rounded-xl bg-slate-900 dark:bg-black text-emerald-300 font-mono text-xs overflow-x-auto border border-emerald-900/40 dark:border-slate-800"
        >
          <code>{codeLines.join('\n')}</code>
        </pre>
      );
      continue;
    }

    // Regular paragraph
    elements.push(
      <p key={elemKey++} className="my-2 text-[13.5px] sm:text-[14px] leading-relaxed text-emerald-950 dark:text-slate-100">
        {renderInline(trimmed)}
      </p>
    );
    i++;
  }

  return <div className="space-y-1.5 text-[13.5px] sm:text-[14px] text-emerald-950 dark:text-slate-100">{elements}</div>;
}
