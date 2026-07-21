import Link from "next/link";

export default function Home() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6">
      {/* Signature element: a quiet knowledge-graph constellation, evoking the
          Career Brain concept without competing with the headline. */}
      <svg
        className="pointer-events-none absolute right-[-80px] top-1/2 hidden -translate-y-1/2 opacity-[0.35] md:block"
        width="420"
        height="420"
        viewBox="0 0 420 420"
        fill="none"
        aria-hidden="true"
      >
        <g stroke="#5B4FE8" strokeWidth="1">
          <line x1="60" y1="80" x2="180" y2="140" />
          <line x1="180" y1="140" x2="150" y2="260" />
          <line x1="180" y1="140" x2="300" y2="120" />
          <line x1="300" y1="120" x2="340" y2="240" />
          <line x1="150" y1="260" x2="260" y2="320" />
          <line x1="150" y1="260" x2="80" y2="330" />
          <line x1="300" y1="120" x2="260" y2="320" />
        </g>
        <g fill="#5B4FE8">
          <circle cx="60" cy="80" r="5" />
          <circle cx="180" cy="140" r="7" />
          <circle cx="300" cy="120" r="5" />
          <circle cx="150" cy="260" r="6" />
          <circle cx="340" cy="240" r="4" />
          <circle cx="260" cy="320" r="6" />
          <circle cx="80" cy="330" r="4" />
        </g>
      </svg>

      <div className="relative z-10 flex max-w-2xl flex-col items-start">
        <span className="font-display text-sm font-semibold uppercase tracking-[0.2em] text-accent">
          MemoryVerse AI
        </span>
        <h1 className="mt-5 font-display text-5xl font-semibold leading-[1.1] text-foreground sm:text-6xl">
          Your Personal Career Intelligence Engine.
        </h1>
        <p className="mt-6 max-w-lg text-lg text-muted">
          Upload your certificates, resumes, and project reports. MemoryVerse
          AI turns them into a Career Brain you can search, question, and
          understand — evidence included.
        </p>
        <Link
          href="/login"
          className="mt-10 inline-flex items-center rounded-full bg-accent px-7 py-3.5 text-sm font-semibold text-accent-foreground transition-colors hover:bg-accent/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Get Started
        </Link>
      </div>
    </main>
  );
}
