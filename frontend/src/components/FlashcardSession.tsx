"use client";

import React, { useState, useEffect } from "react";
import { getDueFlashcards, reviewFlashcard, RecallCard } from "@/lib/api";
import { CheckCircle2, RotateCw, AlertCircle, Sparkles, HelpCircle } from "lucide-react";

const SM2_RATINGS = [
  { rating: 0, label: "0 · Olvido", desc: "Blackout total", color: "hover:border-red-600 hover:text-red-500" },
  { rating: 1, label: "1 · Malo", desc: "Respuesta errónea", color: "hover:border-orange-600 hover:text-orange-500" },
  { rating: 2, label: "2 · Difícil", desc: "Recuerdo con dudas", color: "hover:border-yellow-600 hover:text-yellow-500" },
  { rating: 3, label: "3 · Regular", desc: "Acierto con esfuerzo", color: "hover:border-blue-500 hover:text-blue-400" },
  { rating: 4, label: "4 · Bueno", desc: "Acierto tras pausa", color: "hover:border-green-500 hover:text-green-400" },
  { rating: 5, label: "5 · Perfecto", desc: "Acierto inmediato", color: "hover:border-coral hover:text-coral" },
];

export default function FlashcardSession() {
  const [cards, setCards] = useState<RecallCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadCards = async () => {
    setLoading(true);
    setError(null);
    try {
      const dueCards = await getDueFlashcards();
      setCards(dueCards);
      setCurrentIndex(0);
      setShowAnswer(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al obtener tarjetas";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCards();
  }, []);

  const handleRating = async (rating: number) => {
    if (!cards[currentIndex] || submitting) return;

    setSubmitting(true);
    try {
      await reviewFlashcard(cards[currentIndex].id, rating);
      setShowAnswer(false);
      setCurrentIndex((prev) => prev + 1);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al registrar calificación";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-16 bg-black border border-surface-border text-center">
        <RotateCw className="w-6 h-6 text-cobalt animate-spin mb-4" />
        <span className="font-heading text-xs uppercase tracking-ultra text-neutral-400">
          Cargando Tarjetas de Active Recall...
        </span>
      </div>
    );
  }

  const currentCard = cards[currentIndex];
  const isCompleted = !currentCard || currentIndex >= cards.length;

  if (isCompleted) {
    return (
      <div className="p-12 bg-black border border-surface-border text-center space-y-6">
        <div className="w-12 h-12 bg-surface-card border border-surface-border flex items-center justify-center mx-auto text-coral">
          <CheckCircle2 className="w-6 h-6" />
        </div>
        <div>
          <h3 className="font-heading text-lg uppercase tracking-wide text-white mb-2">
            ¡Repaso Diario Completado!
          </h3>
          <p className="text-neutral-400 text-xs max-w-md mx-auto leading-relaxed">
            No tienes más tarjetas de Active Recall programadas para hoy según el algoritmo SM-2.
            Tus intervalos han sido actualizados en la base de datos.
          </p>
        </div>
        <button
          onClick={loadCards}
          className="inline-flex items-center space-x-2 bg-surface-card hover:bg-surface-elevated text-white border border-surface-border px-6 py-3 font-heading text-xs uppercase tracking-ultra"
        >
          <RotateCw className="w-3.5 h-3.5" />
          <span>Verificar Nuevamente</span>
        </button>
      </div>
    );
  }

  return (
    <div className="bg-black border border-surface-border p-8">
      {/* Session Progress Header */}
      <div className="flex items-center justify-between pb-6 border-b border-surface-border mb-8">
        <div>
          <span className="font-heading text-[10px] uppercase tracking-ultra text-neutral-500 block">
            Sesión de Spaced Repetition (SM-2)
          </span>
          <span className="text-xs font-mono text-white font-bold">
            Tarjeta {currentIndex + 1} de {cards.length}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-500">
            EF: {currentCard.easiness_factor.toFixed(2)} · Intervalo: {currentCard.interval}d
          </span>
        </div>
      </div>

      {/* Card Body */}
      <div className="space-y-6">
        <div className="bg-surface-base p-8 border border-surface-border min-h-[160px] flex flex-col justify-center">
          <span className="text-[9px] font-heading uppercase tracking-ultra text-coral block mb-3">
            Pregunta de Evocación Activa
          </span>
          <h3 className="text-xl font-light text-white leading-relaxed">
            {currentCard.question}
          </h3>

          {currentCard.context_clue && (
            <div className="mt-4 flex items-center space-x-2 text-xs text-neutral-500 font-mono">
              <HelpCircle className="w-3 h-3 text-cobalt" />
              <span>Pista: {currentCard.context_clue}</span>
            </div>
          )}
        </div>

        {/* Reveal or Answer Area */}
        {!showAnswer ? (
          <button
            onClick={() => setShowAnswer(true)}
            className="w-full bg-coral hover:bg-coral-hover text-black py-4 font-heading text-xs uppercase tracking-ultra transition-all"
          >
            Revelar Respuesta
          </button>
        ) : (
          <div className="space-y-6 animate-fadeIn">
            <div className="bg-surface-card p-8 border-l-2 border-cobalt">
              <span className="text-[9px] font-heading uppercase tracking-ultra text-cobalt block mb-3">
                Respuesta / Criterio Clave
              </span>
              <p className="text-base text-neutral-200 leading-relaxed whitespace-pre-wrap">
                {currentCard.answer}
              </p>
            </div>

            {/* SM-2 Quality Rating Buttons */}
            <div>
              <span className="font-heading text-[10px] uppercase tracking-ultra text-neutral-400 block mb-3 text-center">
                Califica tu Esfuerzo de Retención (Algoritmo SM-2)
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
                {SM2_RATINGS.map((item) => (
                  <button
                    key={item.rating}
                    onClick={() => handleRating(item.rating)}
                    disabled={submitting}
                    className={`p-3 bg-surface-base border border-surface-border text-left transition-all ${item.color} disabled:opacity-40`}
                  >
                    <div className="font-heading text-xs uppercase tracking-wider text-white">
                      {item.label}
                    </div>
                    <div className="text-[9px] text-neutral-500 font-mono mt-1">
                      {item.desc}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-6 p-3 bg-red-950/30 border border-red-900 text-coral text-xs font-mono">
          {error}
        </div>
      )}
    </div>
  );
}
