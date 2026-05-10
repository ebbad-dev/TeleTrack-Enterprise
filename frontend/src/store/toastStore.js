import { create } from 'zustand';

let toastIdCounter = 0;

const useToastStore = create((set) => ({
  toasts: [],

  addToast: (toast) => {
    const id = ++toastIdCounter;
    const newToast = {
      id,
      type: toast.type || 'info',
      title: toast.title || '',
      message: toast.message || '',
      duration: toast.duration || 4000,
    };
    set((state) => ({ toasts: [...state.toasts, newToast] }));

    // Auto-remove
    if (newToast.duration > 0) {
      setTimeout(() => {
        set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
      }, newToast.duration);
    }
    return id;
  },

  removeToast: (id) => {
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
  },

  // Convenience methods
  success: (message, title = 'Success') => {
    return useToastStore.getState().addToast({ type: 'success', title, message });
  },
  error: (message, title = 'Error') => {
    return useToastStore.getState().addToast({ type: 'error', title, message, duration: 6000 });
  },
  warning: (message, title = 'Warning') => {
    return useToastStore.getState().addToast({ type: 'warning', title, message });
  },
  info: (message, title = 'Info') => {
    return useToastStore.getState().addToast({ type: 'info', title, message });
  },
}));

export default useToastStore;
