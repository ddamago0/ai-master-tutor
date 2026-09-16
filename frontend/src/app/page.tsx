export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 text-center">
      <div className="max-w-2xl space-y-4">
        <span className="inline-block rounded-full border border-neutral-800 bg-neutral-900 px-3 py-1 text-xs font-mono tracking-wider text-neutral-400">
          PROACTIVE TUTOR ENGINE
        </span>
        <h1 className="text-4xl sm:text-5xl font-light tracking-tight text-neutral-100">
          AI Master Tutor
        </h1>
        <p className="text-neutral-400 text-sm sm:text-base leading-relaxed">
          Sistema de tutoría interactiva de alto rendimiento con Active Recall y Spaced Repetition.
        </p>
      </div>
    </main>
  );
}
