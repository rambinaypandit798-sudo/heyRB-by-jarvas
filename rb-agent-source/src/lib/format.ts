/**
 * Section 1 enforcement: no markdown symbols anywhere in rendered text.
 * Asterisks and hashes are stripped, and every list line becomes a bullet dot.
 */
export function cleanText(input: string): string {
  if (!input) return "";
  const lines = input.replace(/\r/g, "").split("\n");
  const out = lines.map((raw) => {
    let line = raw;
    line = line.replace(/^\s{0,6}#{1,6}\s*/, "");
    line = line.replace(/^\s*>\s?/, "");
    line = line.replace(/^(\s*)(?:[-*+•]|\d{1,2}[.)])\s+/, "$1• ");
    line = line.replace(/\*{1,3}/g, "");
    line = line.replace(/_{2,3}/g, "");
    line = line.replace(/`{1,3}/g, "");
    line = line.replace(/#{1,6}/g, "");
    return line.replace(/[ \t]+$/, "");
  });
  return out.join("\n").replace(/\n{3,}/g, "\n\n").trim();
}

export function chatTitleFrom(text: string) {
  const clean = cleanText(text).replace(/\n/g, " ").trim();
  return clean.length > 48 ? `${clean.slice(0, 48)}…` : clean || "New chat";
}
