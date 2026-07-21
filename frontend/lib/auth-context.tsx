"use client";

/**
 * Auth context — tracks Firebase auth state app-wide and exposes the
 * sign-in/sign-out actions. Any component can call useAuth() instead of
 * talking to the Firebase SDK directly.
 */
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { onAuthStateChanged, signInWithPopup, signOut, type User } from "firebase/auth";

import { getFirebaseAuth, googleProvider } from "@/lib/firebase";
import { apiFetch } from "@/lib/api";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(getFirebaseAuth(), (firebaseUser) => {
      setUser(firebaseUser);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  async function signInWithGoogle() {
    const result = await signInWithPopup(getFirebaseAuth(), googleProvider);
    const idToken = await result.user.getIdToken();

    // Register/sync the user record in Postgres on first (or any) login.
    // Failures here shouldn't block the user from reaching the dashboard —
    // get_current_user re-verifies on every protected call anyway, so a
    // missed sync here just means it happens on the next request instead.
    try {
      await apiFetch("/api/v1/auth/login", { method: "POST" }, idToken);
    } catch (error) {
      console.error("Failed to sync user with backend:", error);
    }
  }

  async function logout() {
    await signOut(getFirebaseAuth());
  }

  return (
    <AuthContext.Provider value={{ user, loading, signInWithGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }
  return context;
}
