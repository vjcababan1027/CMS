import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { authService } from "../services/authService";
import { setAuthToken } from "../services/api";

const AuthContext = createContext(null);

const TOKEN_KEY = "cms_access_token";
const USER_KEY = "cms_user";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
      setAuthToken(token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
      setAuthToken(null);
    }
  }, [token]);

  useEffect(() => {
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
    else localStorage.removeItem(USER_KEY);
  }, [user]);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const tokenRes = await authService.login(email, password);
      const profile = await authService.getMe(tokenRes.access_token);
      setToken(tokenRes.access_token);
      setUser(profile);
      return { ok: true };
    } catch (error) {
      return {
        ok: false,
        message: error?.response?.data?.detail || "Login failed"
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated: Boolean(token),
      login,
      logout
    }),
    [token, user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
