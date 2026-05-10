/**
 * TeleTrack Enterprise — Socket Store
 * WebSocket connection management using Socket.IO.
 * Provides real-time updates for dashboard, alerts, and notifications.
 */

import { create } from 'zustand';
import { io } from 'socket.io-client';

const useSocketStore = create((set, get) => ({
  socket: null,
  connected: false,
  lastDashboardUpdate: null,
  realtimeAlerts: [],

  connect: () => {
    const existing = get().socket;
    if (existing?.connected) return;

    const socket = io(window.location.origin, {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      autoConnect: true,
    });

    socket.on('connect', () => {
      console.log('[TeleTrack] WebSocket connected');
      set({ connected: true });

      // Subscribe to dashboard updates
      socket.emit('subscribe_dashboard');

      // Join user-specific room for notifications
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user?.id) {
        socket.emit('join', { room: `user_${user.id}` });
      }
    });

    socket.on('disconnect', () => {
      console.log('[TeleTrack] WebSocket disconnected');
      set({ connected: false });
    });

    // Listen for real-time events
    socket.on('dashboard_update', (data) => {
      set({ lastDashboardUpdate: data });
    });

    socket.on('device_status_change', (data) => {
      // Dispatch a custom event for components to listen to
      window.dispatchEvent(new CustomEvent('device_status_change', { detail: data }));
    });

    socket.on('new_alert', (data) => {
      set((state) => ({
        realtimeAlerts: [data, ...state.realtimeAlerts].slice(0, 20),
      }));
      window.dispatchEvent(new CustomEvent('new_alert', { detail: data }));
    });

    socket.on('new_notification', (data) => {
      window.dispatchEvent(new CustomEvent('new_notification', { detail: data }));
    });

    set({ socket });
  },

  disconnect: () => {
    const { socket } = get();
    if (socket) {
      socket.disconnect();
      set({ socket: null, connected: false });
    }
  },

  clearAlerts: () => set({ realtimeAlerts: [] }),
}));

export default useSocketStore;
