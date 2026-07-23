/**
 * Authenticated fetch helper for calling the backend API.
 *
 * Attaches a Firebase ID token as a Bearer header on every call.
 * Normally that token comes from auth.currentUser.getIdToken() — but an
 * explicit idToken can be passed for the one moment that matters: right
 * after signInWithPopup(), where the caller already has a fresh token in
 * hand from the sign-in result and shouldn't depend on currentUser being
 * updated yet by the time this runs.
 */
import { getFirebaseAuth } from "@/lib/firebase";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function apiFetch(
  path: string,
  options: RequestInit = {},
  idTokenOverride?: string,
): Promise<Response> {
  const idToken = idTokenOverride ?? (await getFirebaseAuth().currentUser?.getIdToken());

  if (!idToken) {
    throw new Error("apiFetch called with no authenticated user and no idToken override.");
  }

  const headers = new Headers(options.headers ?? undefined);
  headers.set("Authorization", `Bearer ${idToken}`);
  headers.set("Content-Type", "application/json");

  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });
}
