import axios from "axios";
import { api } from "./api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export const authService = {
  async login(email, password) {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    const res = await axios.post(`${API_BASE_URL}/auth/login`, form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    return res.data;
  },

  async getMe(token) {
    const res = await api.get("/users/me", {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.data;
  }
};
