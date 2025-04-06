import React, { useEffect, useState } from "react";

export default function EmotionBreakdown({ breakdown }) {
  const [visibleText, setVisibleText] = useState("");
  const [lines, setLines] = useState([]);
  const [lineIndex, setLineIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);

  useEffect(() => {
    if (!breakdown) return;

    const sortedLines = Object.entries(breakdown)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([emotion, value]) => `${emotion}: ${Math.round(value)}%`);

    setLines(["Analysis Breakdown:", "", ...sortedLines]); // include a title
    setVisibleText("");
    setLineIndex(0);
    setCharIndex(0);
  }, [breakdown]);

  useEffect(() => {
    if (lineIndex >= lines.length) return;

    const currentLine = lines[lineIndex];

    if (charIndex < currentLine.length) {
      const timeout = setTimeout(() => {
        setVisibleText((prev) => prev + currentLine[charIndex]);
        setCharIndex((prev) => prev + 1);
      }, 40);
      return () => clearTimeout(timeout);
    } else {
      const lineBreak = "\n";
      const timeout = setTimeout(() => {
        setVisibleText((prev) => prev + lineBreak);
        setLineIndex((prev) => prev + 1);
        setCharIndex(0);
      }, 500);
      return () => clearTimeout(timeout);
    }
  }, [charIndex, lineIndex, lines]);

  return (
    <pre className="mt-4 text-lg text-gray-300 font-mono whitespace-pre-line">
      {visibleText}
    </pre>
  );
}
