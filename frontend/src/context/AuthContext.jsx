import { createContext, useContext, useEffect, useState } from "react";
import { getMe, login as apiLogin, register as apiRegister } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("pollisync_token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      getMe()
        .then((data) => setUser(data))
        .catch(() => {
          localStorage.removeItem("pollisync_token");
          setToken(null);
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  async function login(email, password) {
    const data = await apiLogin(email, password);
    localStorage.setItem("pollisync_token", data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  }

  async function register(email, password, fullName) {
    const data = await apiRegister(email, password, fullName);
    localStorage.setItem("pollisync_token", data.access_token);
    setToken(data.access_token);
    return data;
  }

  function logout() {
    localStorage.removeItem("pollisync_token");
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
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
