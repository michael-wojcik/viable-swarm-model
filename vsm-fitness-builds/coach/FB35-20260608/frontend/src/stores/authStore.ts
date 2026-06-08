import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User, UserRole } from "@/shared/types";

interface AuthState {
  token: string | null;
  user: User | null;
  role: UserRole | null;
  setAuth: (token: string, user: User) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      role: null,
      setAuth: (token, user) => set({ token, user, role: user.role }),
      clearAuth: () => set({ token: null, user: null, role: null }),
    }),
    {
      name: "fb35-auth-storage",
      skipHydration: true,
    }
  )
);
