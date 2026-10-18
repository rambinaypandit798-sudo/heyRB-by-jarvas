const TRIGGERS = [
  "याद रखो",
  "याद रखना",
  "सेव कर लो",
  "सेव करलो",
  "सेव कर दो",
  "यह चीज़ सेव कर लो",
  "ये सेव कर लो",
  "remember this",
  "remember that",
  "save this",
  "keep this in mind",
  "note this down",
  "don't forget",
];

export function hasMemoryTrigger(text: string) {
  const lower = text.toLowerCase();
  return TRIGGERS.some((t) => lower.includes(t.toLowerCase()));
}
