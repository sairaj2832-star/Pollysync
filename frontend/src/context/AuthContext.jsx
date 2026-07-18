import { createContext, useContext, useEffect, useState } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  updateProfile,
} from "firebase/auth";
import { firebaseAuth as apiFirebaseAuth, getMe, login as apiLogin, logout as apiLogout, register as apiRegister } from "../lib/api";
import { firebaseAuth, googleProvider, isFirebaseConfigured } from "../lib/firebase";

const AuthContext = createContext(null);
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe()
      .then((data) => setUser(data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  function setUserFromData(data) {
    setUser(data.user);
  }

  async function exchangeFirebaseSession(firebaseUser) {
    const idToken = await firebaseUser.getIdToken();
    const data = await apiFirebaseAuth(idToken);
    setUserFromData(data);
    return data;
  }

  async function login(email, password) {
    if (USE_MOCK) {
      const data = await apiLogin(email, password);
      setUserFromData(data);
      return data;
    }
    if (!isFirebaseConfigured || !firebaseAuth) {
      throw new Error("Firebase auth is not configured in the frontend environment.");
    }
    try {
      const credential = await signInWithEmailAndPassword(firebaseAuth, email, password);
      return await exchangeFirebaseSession(credential.user);
    } catch (err) {
      if (err?.code?.startsWith("auth/")) throw err;
      throw new Error(err?.message || "Login failed");
    }
  }

  async function register(email, password, fullName) {
    if (USE_MOCK) {
      const data = await apiRegister(email, password, fullName);
      setUserFromData(data);
      return data;
    }
    if (!isFirebaseConfigured || !firebaseAuth) {
      throw new Error("Firebase auth is not configured in the frontend environment.");
    }
    try {
      const credential = await createUserWithEmailAndPassword(firebaseAuth, email, password);
      if (fullName) {
        await updateProfile(credential.user, { displayName: fullName });
      }
      return await exchangeFirebaseSession(credential.user);
    } catch (err) {
      if (err?.code?.startsWith("auth/")) throw err;
      throw new Error(err?.message || "Registration failed");
    }
  }

  async function loginWithGoogle() {
    if (USE_MOCK) {
      return login("ananya@greenridge.farm", "demo");
    }
    if (!isFirebaseConfigured || !firebaseAuth || !googleProvider) {
      throw new Error("Firebase Google auth is not configured in the frontend environment.");
    }
    try {
      googleProvider.setCustomParameters({ prompt: "select_account" });
      const credential = await signInWithPopup(firebaseAuth, googleProvider);
      return await exchangeFirebaseSession(credential.user);
    } catch (err) {
      if (err?.code?.startsWith("auth/")) throw err;
      throw new Error(err?.message || "Google sign-in failed");
    }
  }

  async function refreshUser() {
    try {
      const data = await getMe();
      setUser(data);
      return data;
    } catch {
      return null;
    }
  }

  function setOnboarded() {
    setUser((prev) => (prev ? { ...prev, has_onboarded: true } : prev));
  }

  async function logout() {
    try {
      await apiLogout();
    } catch {
    }
    if (firebaseAuth) {
      try {
        await signOut(firebaseAuth);
      } catch {
      }
    }
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        loginWithGoogle,
        logout,
        refreshUser,
        setOnboarded,
        isFirebaseConfigured: USE_MOCK || isFirebaseConfigured,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
