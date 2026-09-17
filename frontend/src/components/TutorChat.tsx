"use client";

import React, { useState, useRef, useEffect } from "react";
import { askTutor, TutorResponse } from "@/lib/api";
import { Send, Sparkles, Database, Loader2, BookOpen } from "lucide-react";

interface ChatMessage {
  id: string;
  sender: "user" | "tutor";
  text: string;
  cached?: boolean;
  cacheType?: string | null;
  sources?: TutorResponse["sources"];
  timestamp: string;
}

export default function TutorChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      sender: "tutor",
      text: "Bienvenido a tu sesión de estudio. Pregúntame sobre cualquier concepto de tus clases o pídemelo para iniciar un desafío de Active Recall.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const query = input.trim();
    if (!query || loading) return;

    setInput("");
    setError(null);

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await askTutor(query);
      const tutorMessage: ChatMessage = {
        id: `tutor-${Date.now()}`,
        sender: "tutor",
        text: response.answer,
        cached: response.cached,
        cacheType: response.cache_type,
        sources: response.sources,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, tutorMessage]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al conectar con el tutor";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[650px] bg-black border border-surface-border rounded-none">
      {/* Chat Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-surface-border bg-surface-base">
        <div className="flex items-center space-x-3">
          <div className="w-2.5 h-2.5 bg-coral animate-pulse" />
          <h2 className="font-heading text-xs uppercase tracking-ultra text-white">
            Tutor Interactivo · Active Recall
          </h2>
        </div>
        <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-500">
          Costo Cero · RAG Híbrido
        </span>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${m.sender === "user" ? "items-end" : "items-start"}`}
          >
            <div
              className={`max-w-[85%] p-4 text-sm leading-relaxed ${
                m.sender === "user"
                  ? "bg-surface-elevated text-white border-l-2 border-coral"
                  : "bg-surface-card text-neutral-200 border-l-2 border-cobalt"
              }`}
            >
              {/* Metadata badge for Tutor answers */}
              {m.sender === "tutor" && (
                <div className="flex items-center space-x-2 mb-2">
                  {m.cached ? (
                    <span className="inline-flex items-center space-x-1 bg-cobalt text-white text-[9px] font-mono uppercase tracking-wider px-2 py-0.5 font-bold">
                      <Database className="w-2.5 h-2.5 mr-1" />
                      Caché Semántico (0ms)
                    </span>
                  ) : (
                    <span className="inline-flex items-center space-x-1 bg-neutral-900 border border-neutral-800 text-neutral-400 text-[9px] font-mono uppercase tracking-wider px-2 py-0.5">
                      <Sparkles className="w-2.5 h-2.5 mr-1 text-coral" />
                      Inferencia Fresca
                    </span>
                  )}
                  <span className="text-[10px] text-neutral-500 font-mono">{m.timestamp}</span>
                </div>
              )}

              <p className="whitespace-pre-wrap">{m.text}</p>

              {/* Display referenced RAG sources */}
              {m.sources && m.sources.length > 0 && (
                <div className="mt-4 pt-3 border-t border-neutral-900">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-500 block mb-1">
                    Fuentes Citadas:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {m.sources.map((s, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center text-[10px] text-neutral-400 bg-black border border-neutral-800 px-2 py-1"
                      >
                        <BookOpen className="w-2.5 h-2.5 mr-1 text-cobalt" />
                        {s.title} ({Math.round(s.similarity_score * 100)}% match)
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-3 p-4 bg-surface-card border-l-2 border-cobalt max-w-[50%]">
            <Loader2 className="w-4 h-4 text-cobalt animate-spin" />
            <span className="text-xs font-mono uppercase tracking-wider text-neutral-400">
              Consultando RAG y LLM Gateway...
            </span>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-950/30 border border-red-900 text-coral text-xs font-mono">
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Field */}
      <form onSubmit={handleSend} className="p-4 bg-surface-base border-t border-surface-border">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Pregunta o pon a prueba tu recuerdo activo..."
            className="flex-1 bg-black border border-surface-border text-white text-sm px-4 py-3 focus:outline-none focus:border-coral transition-colors"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-coral hover:bg-coral-hover text-black px-6 py-3 font-heading text-xs uppercase tracking-ultra flex items-center space-x-2 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            <span>Consultar</span>
            <Send className="w-3 h-3" />
          </button>
        </div>
      </form>
    </div>
  );
}
