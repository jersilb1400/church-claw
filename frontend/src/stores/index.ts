/** Global state management with Zustand */

import { create } from 'zustand';
import type { User, Agent } from '../types';

interface AuthStore {
    user: User | null;
    setUser: (user: User | null) => void;
    logout: () => Promise<void>;
    isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
    user: null,

    setUser: (user) => set({ user }),

    logout: async () => {
        try {
            await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
        } catch {
            /* ignore network errors */
        }
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        set({ user: null });
    },

    isAuthenticated: () => !!get().user,
}));

interface AppStore {
    sidebarCollapsed: boolean;
    toggleSidebar: () => void;
    selectedAgentId: string | null;
    setSelectedAgent: (id: string | null) => void;
}

export const useAppStore = create<AppStore>((set) => ({
    sidebarCollapsed: false,
    toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
    selectedAgentId: null,
    setSelectedAgent: (id) => set({ selectedAgentId: id }),
}));
