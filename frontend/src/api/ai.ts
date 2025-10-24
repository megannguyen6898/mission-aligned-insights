import { api } from "@/lib/api";

export type ChatRole = "user" | "ai";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface AskAIResponse {
  answer: string;
}

export async function askAI(
  question: string,
  history: ChatMessage[] = [],
  context?: string
): Promise<AskAIResponse> {
  const { data } = await api.post<AskAIResponse>("/ai/ask", {
    question,
    history,
    context,
  });
  return data;
}
