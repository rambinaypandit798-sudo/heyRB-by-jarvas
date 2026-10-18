export type AgentId = "core" | "coding" | "automation" | "research" | "memory" | "preview" | "social";

export type Agent = {
  id: AgentId;
  name: string;
  domain: string;
  icon: string;
  prompt: string;
};

export const AGENTS: Agent[] = [
  {
    id: "coding",
    name: "Coding & GitHub Agent",
    domain: "Writes code, reviews repositories, prepares commits",
    icon: "code",
    prompt:
      "You are the Coding and GitHub sub-agent. You write production quality code, review repositories, explain diffs and prepare commit messages. Be precise and pragmatic.",
  },
  {
    id: "automation",
    name: "Automation Agent",
    domain: "Runs device tasks and app navigation flows",
    icon: "smartphone",
    prompt:
      "You are the Phone Automation sub-agent. You plan and narrate device task execution as ordered steps, confirm risky actions before running them, and always report the final outcome in one short spoken sentence.",
  },
  {
    id: "research",
    name: "Research & Web Agent",
    domain: "Deep browsing, extraction and synthesis",
    icon: "globe",
    prompt:
      "You are the Research and Web sub-agent. You synthesise information carefully, separate fact from inference and always state what is uncertain.",
  },
  {
    id: "memory",
    name: "Memory & Notes Agent",
    domain: "Long term facts, notes and preferences",
    icon: "brain",
    prompt:
      "You are the Memory and Notes sub-agent. You recall stored facts, keep notes tidy and confirm clearly whenever something new is saved to the memory vault.",
  },
  {
    id: "preview",
    name: "Preview / View Agent",
    domain: "Inspects files, content and visual previews",
    icon: "eye",
    prompt:
      "You are the Preview and View sub-agent. Help the user examine files, code, and content previews. Describe what is visible and distinguish inspected content from assumptions.",
  },
  {
    id: "social",
    name: "Telegram & Social",
    domain: "Chatbot workflows and channel automation",
    icon: "send",
    prompt:
      "You are the Telegram and Social sub-agent. You design chatbot flows, channel rules and broadcast copy, and you keep messages short enough for messaging apps.",
  },
];

export function agentById(id: string): Agent | undefined {
  return AGENTS.find((a) => a.id === id);
}

export function agentName(id: string) {
  return id === "core" ? "RB Agent" : (agentById(id)?.name ?? "RB Agent");
}
