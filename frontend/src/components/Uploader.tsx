"use client";

import React, { useState } from "react";
import { ingestDocument } from "@/lib/api";
import { UploadCloud, CheckCircle2, FileText, Loader2, AlertCircle } from "lucide-react";

export default function Uploader() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = (file: File) => {
    if (!title) {
      setTitle(file.name.replace(/\.[^/.]+$/, ""));
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      setContent(text || "");
    };
    reader.readAsText(file);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim() || loading) return;

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await ingestDocument({
        title: title.trim(),
        raw_content: content.trim(),
        source_type: "manual",
      });
      setSuccess(true);
      setTitle("");
      setContent("");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error durante la ingesta";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-black border border-surface-border p-8">
      <div className="mb-6">
        <h3 className="font-heading text-xs uppercase tracking-ultra text-white mb-2">
          Ingesta Manual de Material de Estudio
        </h3>
        <p className="text-neutral-400 text-xs leading-relaxed">
          Carga lecturas, diapositivas o apuntes en texto plano o arrastra archivos para generar
          embeddings vectoriales (768 dims) en PostgreSQL.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Drag & Drop Zone */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          className={`border-2 border-dashed p-8 text-center transition-all ${
            dragOver
              ? "border-coral bg-surface-card"
              : "border-surface-border bg-surface-base hover:border-neutral-700"
          }`}
        >
          <UploadCloud className="w-8 h-8 text-neutral-500 mx-auto mb-3" />
          <div className="text-xs font-mono uppercase tracking-wider text-neutral-300 mb-1">
            Arrastra tu archivo aquí o haz clic para seleccionarlo
          </div>
          <p className="text-[10px] text-neutral-500 font-mono">
            Soporta archivos de texto (.txt, .md, apuntes en texto)
          </p>
          <input
            type="file"
            accept=".txt,.md,.text"
            className="hidden"
            id="file-input"
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                handleFile(e.target.files[0]);
              }
            }}
          />
          <label
            htmlFor="file-input"
            className="mt-4 inline-block bg-surface-card hover:bg-surface-elevated text-white border border-surface-border px-4 py-2 text-[10px] font-heading uppercase tracking-ultra cursor-pointer"
          >
            Examinar Archivo
          </label>
        </div>

        {/* Inputs */}
        <div className="space-y-4">
          <div>
            <label className="block text-[10px] font-heading uppercase tracking-ultra text-neutral-400 mb-2">
              Título del Material / Módulo
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ej: Biología Celular - Ciclo de Krebs"
              className="w-full bg-black border border-surface-border text-white text-sm px-4 py-3 focus:outline-none focus:border-coral transition-colors"
              required
            />
          </div>

          <div>
            <label className="block text-[10px] font-heading uppercase tracking-ultra text-neutral-400 mb-2">
              Contenido de Estudio
            </label>
            <textarea
              rows={8}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Pega aquí el contenido de la lectura, resumen o diapositivas..."
              className="w-full bg-black border border-surface-border text-white text-sm p-4 focus:outline-none focus:border-coral transition-colors font-mono"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !title.trim() || !content.trim()}
          className="w-full bg-coral hover:bg-coral-hover text-black py-4 font-heading text-xs uppercase tracking-ultra flex items-center justify-center space-x-2 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Procesando Chunks y Embeddings...</span>
            </>
          ) : (
            <>
              <FileText className="w-4 h-4" />
              <span>Indexar Material al Sistema</span>
            </>
          )}
        </button>
      </form>

      {success && (
        <div className="mt-6 p-4 bg-emerald-950/30 border border-emerald-800 text-emerald-400 text-xs font-mono flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>¡Documento indexado con éxito! Ya está disponible en la base de datos de pgvector.</span>
        </div>
      )}

      {error && (
        <div className="mt-6 p-4 bg-red-950/30 border border-red-900 text-coral text-xs font-mono flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
