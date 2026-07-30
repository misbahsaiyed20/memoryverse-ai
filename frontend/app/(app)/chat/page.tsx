"use client";

import { useEffect, useRef, useState } from "react";
import { MessageCircle, Send, FileText } from "lucide-react";

import { askVerse, type VerseSource } from "@/lib/verse-api";
import { cn } from "@/lib/utils";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  sources?: VerseSource[];
}

const SUGGESTED_QUESTIONS = [
  "What skills do I have?",
  "Which projects use Python?",
  "Summarize my work experience.",
  "What certifications have I earned?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  async function send(question: string) {
    if (!question.trim() || sending) return;
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setSending(true);

    try {
      const result = await askVerse(question);
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", text: result.answer, sources: result.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: err instanceof Error ? err.message : "Something went wrong.",
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="flex h-screen flex-col px-6 py-10 sm:px-10">
      <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col">
        <h1 className="font-display text-3xl font-semibold text-foreground">Verse AI</h1>
        <p className="mt-1.5 text-sm text-muted">
          Answers only from your uploaded documents, always with citations.
        </p>

        <div className="mt-6 flex-1 space-y-4 overflow-y-auto pr-1">
          {messages.length === 0 && (
            <div className="rounded-2xl border border-dashed border-border p-6">
              <p className="flex items-center gap-2 text-sm font-medium text-foreground">
                <MessageCircle size={16} className="text-accent" />
                Try asking:
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {SUGGESTED_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => send(q)}
                    className="rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-muted hover:border-accent hover:text-accent"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={cn("flex", message.role === "user" ? "justify-end" : "justify-start")}
            >
              <div
                className={cn(
                  "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
                  message.role === "user"
                    ? "bg-accent text-accent-foreground"
                    : "border border-border bg-surface text-foreground",
                )}
              >
                <p>{message.text}</p>
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5 border-t border-border pt-2.5">
                    {message.sources.map((source, i) => (
                      <span
                        key={`${source.chunk_id}-${i}`}
                        className="inline-flex items-center gap-1 rounded-full bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent"
                      >
                        <FileText size={11} />
                        {source.filename ?? "source"}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {sending && (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-border bg-surface px-4 py-3 text-sm text-muted">
                Thinking…
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="mt-4 flex items-center gap-2 rounded-2xl border border-border bg-surface px-4 py-3 focus-within:border-accent"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your career history…"
            className="flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-muted"
          />
          <button
            type="submit"
            disabled={sending || !input.trim()}
            className="rounded-full bg-accent p-2 text-accent-foreground transition-opacity disabled:opacity-40"
          >
            <Send size={15} />
          </button>
        </form>
      </div>
    </main>
  );
}
