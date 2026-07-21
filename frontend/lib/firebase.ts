/**
 * Firebase client SDK initialization.
 *
 * Lazily initialized (not at module load time). Firebase's SDK validates
 * config as soon as getAuth() is called, and Next.js evaluates client
 * component modules during its server-side prerender pass too — so an
 * eager top-level getAuth() call would crash the build whenever
 * NEXT_PUBLIC_FIREBASE_* isn't set yet. Deferring the call to first
 * actual use (always from a useEffect/event handler, i.e. browser-only)
 * avoids that entirely.
 *
 * All config values come from NEXT_PUBLIC_* env vars (see .env.example).
 * These are safe to expose in the browser bundle — Firebase's security
 * model relies on token verification and rules, not on hiding this config.
 */
import { initializeApp, getApps, getApp, type FirebaseApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, type Auth } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

let firebaseApp: FirebaseApp | undefined;
let authInstance: Auth | undefined;

function getFirebaseApp(): FirebaseApp {
  if (!firebaseApp) {
    firebaseApp = getApps().length ? getApp() : initializeApp(firebaseConfig);
  }
  return firebaseApp;
}

export function getFirebaseAuth(): Auth {
  if (!authInstance) {
    authInstance = getAuth(getFirebaseApp());
  }
  return authInstance;
}

export const googleProvider = new GoogleAuthProvider();
