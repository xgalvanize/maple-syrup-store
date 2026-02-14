import React, { createContext, useContext, useMemo, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));

  const value = useMemo(() => ({
    token,
    isLoggedIn: Boolean(token),
    login: (newToken) => {
      localStorage.setItem("token", newToken);
      setToken(newToken);
    },
    logout: () => {
      localStorage.removeItem("token");
      setToken(null);
    },
  }), [token]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
