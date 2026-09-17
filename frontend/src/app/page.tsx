"use client";

import React, { useState } from "react";
import TutorChat from "@/components/TutorChat";
import FlashcardSession from "@/components/FlashcardSession";
import Uploader from "@/components/Uploader";
import { Brain, MessageSquare, Upload, Zap, ShieldCheck } from "lucide-react";

type ActiveTab = "recall" | "chat" | "upload";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("recall");

  return (
    <div className="min-h-screen bg-black text-white flex flex-col selection:bg-coral selection:text-black">
      {/* Top Editorial Navigation Bar */}
      <header className="border-b border-surface-border bg-black sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-coral" />
            <span className="font-heading text-sm uppercase tracking-ultra font-black">
              AI Master Tutor
            </span>
            <span className="text-[10px] font-mono text-neutral-500 uppercase tracking-wider pl-2 border-l border-neutral-800">
              Zero-Cost Architecture
            </span>
          </div>

          {/* Quick Metrics Bar */}
          <div className="flex items-center space-x-6 text-xs font-mono">
            <div className="flex items-center space-x-2">
              <Zap className="w-3.5 h-3.5 text-coral" />
              <span className="text-neutral-400">Motor:</span>
              <span className="text-white font-bold">Groq / Gemini Flash</span>
            </div>
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-3.5 h-3.5 text-cobalt" />
              <span className="text-neutral-400">Vectores:</span>
              <span className="text-white font-bold">pgvector (768d)</span>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="max-w-7xl mx-auto px-6 flex space-x-1 border-t border-surface-border/50">
          <button
            onClick={() => setActiveTab("recall")}
            className={`py-4 px-6 font-heading text-xs uppercase tracking-ultra flex items-center space-x-2 transition-all border-b-2 ${
              activeTab === "recall"
                ? "border-coral text-white bg-surface-elevated/40"
                : "border-transparent text-neutral-500 hover:text-neutral-300"
            }`}
          >
            <Brain className="w-3.5 h-3.5 text-coral" />
            <span>Active Recall (SM-2)</span>
          </button>

          <button
            onClick={() => setActiveTab("chat")}
            className={`py-4 px-6 font-heading text-xs uppercase tracking-ultra flex items-center space-x-2 transition-all border-b-2 ${
              activeTab === "chat"
                ? "border-cobalt text-white bg-surface-elevated/40"
                : "border-transparent text-neutral-500 hover:text-neutral-300"
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5 text-cobalt" />
            <span>Tutor Socrático</span>
          </button>

          <button
            onClick={() => setActiveTab("upload")}
            className={`py-4 px-6 font-heading text-xs uppercase tracking-ultra flex items-center space-x-2 transition-all border-b-2 ${
              activeTab === "upload"
                ? "border-neutral-200 text-white bg-surface-elevated/40"
                : "border-transparent text-neutral-500 hover:text-neutral-300"
            }`}
          >
            <Upload className="w-3.5 h-3.5 text-neutral-400" />
            <span>Ingesta de Material</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
        {activeTab === "recall" && (
          <div className="space-y-6 animate-fadeIn">
            <div className="border-l-2 border-coral pl-4 py-1">
              <h1 className="font-heading text-xl uppercase tracking-wider text-white">
                Sesión de Retención Activa
              </h1>
              <p className="text-xs text-neutral-400 mt-1 font-mono">
                Preguntas de evocación espaciada calculadas matemáticamente para optimizar la memoria a largo plazo.
              </p>
            </div>
            <FlashcardSession />
          </div>
        )}

        {activeTab === "chat" && (
          <div className="space-y-6 animate-fadeIn">
            <div className="border-l-2 border-cobalt pl-4 py-1">
              <h1 className="font-heading text-xl uppercase tracking-wider text-white">
                Tutor Socrático Interactivo
              </h1>
              <p className="text-xs text-neutral-400 mt-1 font-mono">
                Asistente pedagógico conectado a tu base de conocimientos con RAG híbrido y caché semántico.
              </p>
            </div>
            <TutorChat />
          </div>
        )}

        {activeTab === "upload" && (
          <div className="space-y-6 animate-fadeIn">
            <div className="border-l-2 border-neutral-600 pl-4 py-1">
              <h1 className="font-heading text-xl uppercase tracking-wider text-white">
                Carga y Gestión de Conocimiento
              </h1>
              <p className="text-xs text-neutral-400 mt-1 font-mono">
                Agrega manualmente apuntes o lecturas complementarias a los extraídos desde la extensión de Chrome.
              </p>
            </div>
            <Uploader />
          </div>
        )}
      </main>

      {/* Minimal Footer */}
      <footer className="border-t border-surface-border py-6 px-8 text-center text-xs font-mono text-neutral-600">
        AI MASTER TUTOR · HIGH RETENTION ZERO-COST LEARNING ENGINE
      </footer>
    </div>
  );
}
