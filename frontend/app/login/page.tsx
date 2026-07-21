"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { useAuth } from "@/lib/auth-context";
import { GoogleIcon } from "@/components/google-icon";

export default function LoginPage() {
  const { user, loading, signInWithGoogle } = useAuth();
  const router = useRouter();
  const [signingIn, setSigningIn] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Already signed in? Skip straight to the dashboard.
  useEffect(() => {
    if (!loading && user) {
      router.replace("/dashboard");
    }
  }, [loading, user, router]);

  async function handleSignIn() {
    setError(null);
    setSigningIn(true);
    try {
      await signInWithGoogle();
      router.replace("/dashboard");
    } catch {
      setError("Sign-in didn't go through. Please try again.");
    } finally {
      setSigningIn(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <Link href="/" className="font-display text-sm font-semibold uppercase tracking-[0.2em] text-accent">
          MemoryVerse AI
        </Link>
        <h1 className="mt-4 font-display text-3xl font-semibold text-foreground">
          Welcome back
        </h1>
        <p className="mt-2 text-muted">
          Sign in to continue building your Career Brain.
        </p>

        <button
          onClick={handleSignIn}
          disabled={signingIn}
          className="mt-8 flex w-full items-center justify-center gap-3 rounded-full border border-border bg-surface px-6 py-3.5 text-sm font-semibold text-foreground transition-colors hover:bg-accent-soft disabled:cursor-not-allowed disabled:opacity-60"
        >
          <GoogleIcon />
          {signingIn ? "Signing in…" : "Continue with Google"}
        </button>

        {error && (
          <p className="mt-4 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
      </div>
    </main>
  );
}
