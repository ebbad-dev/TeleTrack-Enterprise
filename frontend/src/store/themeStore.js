/**
 * TeleTrack Enterprise — Theme Store
 * Dark/Light mode toggle with localStorage persistence.
 */

import { create } from 'zustand';

const useThemeStore = create((set) => ({
  theme: localStorage.getItem('teletrack-theme') || 'dark',
  
  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('teletrack-theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    return { theme: newTheme };
  }),

  setTheme: (theme) => {
    localStorage.setItem('teletrack-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    set({ theme });
  },

  initTheme: () => {
    const savedTheme = localStorage.getItem('teletrack-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    set({ theme: savedTheme });
  },
}));

export default useThemeStore;
