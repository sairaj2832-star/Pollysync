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
const ACCESS_TOKEN_KEY = "pollisync_token";
const REFRESH_TOKEN_KEY = "pollisync_refresh_token";
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

function storeSession(data) {
  localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
}

function clearSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem(ACCESS_TOKEN_KEY));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      getMe()
        .then((data) => setUser(data))
        .catch(() => {
          clearSession();
          setToken(null);
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  async function exchangeFirebaseSession(firebaseUser) {
    const idToken = await firebaseUser.getIdToken();
    const data = await apiFirebaseAuth(idToken);
    storeSession(data);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  }

  async function login(email, password) {
    if (USE_MOCK) {
      const data = await apiLogin(email, password);
      storeSession(data);
      setToken(data.access_token);
      setUser(data.user);
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
      storeSession(data);
      setToken(data.access_token);
      setUser(data.user);
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
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (refreshToken) {
      try {
        await apiLogout(refreshToken);
      } catch {
      }
    }
    if (firebaseAuth) {
      try {
        await signOut(firebaseAuth);
      } catch {
      }
    }
    clearSession();
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
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
