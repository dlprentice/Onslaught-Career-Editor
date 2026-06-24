import type { ReactNode } from "react";

export interface MarkdownHeading {
  level: number;
  title: string;
  id: string;
}

export interface MarkdownLinkClick {
  href: string;
  text: string;
}

export interface MarkdownRendererProps {
  markdown: string;
  onLinkClick?: (link: MarkdownLinkClick) => void;
}

export function markdownPlainText(value: string) {
  return value
    .replace(/^#+\s+/, "")
    .replace(/[*_`~]/g, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .trim();
}

function headingSlug(value: string) {
  return markdownPlainText(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function markdownHeadingId(value: string) {
  const cleaned = value.replace(/^#/, "").trim();
  return cleaned.startsWith("doc-") ? cleaned : `doc-${headingSlug(cleaned)}`;
}

export function extractMarkdownHeadings(markdown: string): MarkdownHeading[] {
  return markdown
    .split(/\r?\n/)
    .map((line) => line.match(/^(#{1,3})\s+(.+)$/))
    .filter((match): match is RegExpMatchArray => match !== null)
    .map((match) => ({
      level: match[1].length,
      title: markdownPlainText(match[2]),
      id: markdownHeadingId(match[2])
    }));
}

export function MarkdownRenderer({ markdown, onLinkClick }: MarkdownRendererProps) {
  return <>{renderMarkdownDocument(markdown, onLinkClick)}</>;
}

function renderInlineMarkdown(text: string, onLinkClick?: (link: MarkdownLinkClick) => void): ReactNode[] {
  return text.split(/(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))/g).map((part, index) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={index} className="rounded bg-[#ece7dc] px-1.5 py-0.5 font-mono text-[0.92em] text-[#7a4d0f]">
          {part.slice(1, -1)}
        </code>
      );
    }

    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={index} className="font-semibold text-[#111827]">
          {part.slice(2, -2)}
        </strong>
      );
    }

    const link = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (link) {
      return (
        <a
          key={index}
          data-testid="markdown-link"
          data-link-href={link[2]}
          className="font-medium text-[#245ea8] underline decoration-[#91b5e4] underline-offset-4 hover:text-[#163d73]"
          href={link[2]}
          onClick={(event) => {
            if (!onLinkClick) return;
            event.preventDefault();
            onLinkClick({ href: link[2], text: link[1] });
          }}
        >
          {link[1]}
        </a>
      );
    }

    return part;
  });
}

function renderMarkdownTable(lines: string[], key: string, onLinkClick?: (link: MarkdownLinkClick) => void) {
  const rows = lines
    .filter((line) => !/^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line))
    .map((line) =>
      line
        .trim()
        .replace(/^\|/, "")
        .replace(/\|$/, "")
        .split("|")
        .map((cell) => cell.trim())
    );

  if (rows.length === 0) return null;

  const [head, ...body] = rows;
  return (
    <div key={key} className="my-6 overflow-x-auto rounded-lg border border-[#d8dde6] bg-white">
      <table className="min-w-full divide-y divide-[#d8dde6] text-left text-[0.92rem]">
        <thead className="bg-[#eef2f6] text-[#172033]">
          <tr>
            {head.map((cell, index) => (
              <th key={`${key}-h-${index}`} className="px-4 py-3 font-semibold">
                {renderInlineMarkdown(cell, onLinkClick)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-[#e3e7ee] text-[#2f3947]">
          {body.map((row, rowIndex) => (
            <tr key={`${key}-r-${rowIndex}`}>
              {row.map((cell, cellIndex) => (
                <td key={`${key}-r-${rowIndex}-c-${cellIndex}`} className="px-4 py-3 align-top">
                  {renderInlineMarkdown(cell, onLinkClick)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function renderMarkdownDocument(markdown: string, onLinkClick?: (link: MarkdownLinkClick) => void) {
  const lines = markdown.split(/\r?\n/);
  const blocks = [];
  let index = 0;
  let blockIndex = 0;

  while (index < lines.length) {
    const line = lines[index];
    const trimmed = line.trim();

    if (!trimmed) {
      index++;
      continue;
    }

    if (trimmed.startsWith("```")) {
      const codeLines = [];
      index++;
      while (index < lines.length && !lines[index].trim().startsWith("```")) {
        codeLines.push(lines[index]);
        index++;
      }
      index++;
      blocks.push(
        <pre
          key={`code-${blockIndex++}`}
          className="my-6 overflow-x-auto rounded-lg border border-[#d8dde6] bg-[#111827] p-4 font-mono text-[0.86rem] leading-6 text-[#e5e7eb]"
        >
          {codeLines.join("\n")}
        </pre>
      );
      continue;
    }

    const heading = trimmed.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      const title = markdownPlainText(heading[2]);
      const id = markdownHeadingId(heading[2]);
      if (level === 1) {
        blocks.push(
          <h1 key={`heading-${blockIndex++}`} id={id} className="mt-2 scroll-mt-8 text-4xl font-semibold leading-tight text-[#111827]">
            {title}
          </h1>
        );
      } else if (level === 2) {
        blocks.push(
          <h2 key={`heading-${blockIndex++}`} id={id} className="mt-10 scroll-mt-8 text-2xl font-semibold leading-snug text-[#172033]">
            {title}
          </h2>
        );
      } else {
        blocks.push(
          <h3 key={`heading-${blockIndex++}`} id={id} className="mt-8 scroll-mt-8 text-xl font-semibold leading-snug text-[#172033]">
            {title}
          </h3>
        );
      }
      index++;
      continue;
    }

    if (/^[-*]\s+/.test(trimmed)) {
      const items = [];
      while (index < lines.length && /^[-*]\s+/.test(lines[index].trim())) {
        items.push(lines[index].trim().replace(/^[-*]\s+/, ""));
        index++;
      }
      blocks.push(
        <ul key={`list-${blockIndex++}`} className="my-5 list-disc space-y-2 pl-7 text-[1rem] leading-8 text-[#2f3947]">
          {items.map((item, itemIndex) => (
            <li key={`li-${blockIndex}-${itemIndex}`}>{renderInlineMarkdown(item, onLinkClick)}</li>
          ))}
        </ul>
      );
      continue;
    }

    if (/^\d+\.\s+/.test(trimmed)) {
      const items = [];
      while (index < lines.length && /^\d+\.\s+/.test(lines[index].trim())) {
        items.push(lines[index].trim().replace(/^\d+\.\s+/, ""));
        index++;
      }
      blocks.push(
        <ol key={`ordered-${blockIndex++}`} className="my-5 list-decimal space-y-2 pl-7 text-[1rem] leading-8 text-[#2f3947]">
          {items.map((item, itemIndex) => (
            <li key={`oli-${blockIndex}-${itemIndex}`}>{renderInlineMarkdown(item, onLinkClick)}</li>
          ))}
        </ol>
      );
      continue;
    }

    if (trimmed.includes("|")) {
      const tableLines = [];
      while (index < lines.length && lines[index].trim().includes("|")) {
        tableLines.push(lines[index]);
        index++;
      }
      blocks.push(renderMarkdownTable(tableLines, `table-${blockIndex++}`, onLinkClick));
      continue;
    }

    if (/^---+$/.test(trimmed)) {
      blocks.push(<hr key={`hr-${blockIndex++}`} className="my-8 border-[#d8dde6]" />);
      index++;
      continue;
    }

    const paragraph = [trimmed];
    index++;
    while (
      index < lines.length &&
      lines[index].trim() &&
      !/^(#{1,4})\s+/.test(lines[index].trim()) &&
      !/^[-*]\s+/.test(lines[index].trim()) &&
      !/^\d+\.\s+/.test(lines[index].trim()) &&
      !lines[index].trim().startsWith("```") &&
      !lines[index].trim().includes("|")
    ) {
      paragraph.push(lines[index].trim());
      index++;
    }
    blocks.push(
      <p key={`paragraph-${blockIndex++}`} className="my-5 text-[1.02rem] leading-8 text-[#2f3947]">
        {renderInlineMarkdown(paragraph.join(" "), onLinkClick)}
      </p>
    );
  }

  return blocks;
}
