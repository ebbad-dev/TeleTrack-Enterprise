import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import useToastStore from '../../store/toastStore';

const iconMap = {
  success: <CheckCircle size={20} className="text-success" />,
  error: <XCircle size={20} className="text-error" />,
  warning: <AlertTriangle size={20} className="text-warning" />,
  info: <Info size={20} className="text-primary" />,
};

const borderMap = {
  success: 'border-l-success',
  error: 'border-l-error',
  warning: 'border-l-warning',
  info: 'border-l-primary',
};

const glowMap = {
  success: 'shadow-[0_0_15px_rgba(0,255,102,0.15)]',
  error: 'shadow-[0_0_15px_rgba(255,0,60,0.15)]',
  warning: 'shadow-[0_0_15px_rgba(255,179,0,0.15)]',
  info: 'shadow-[0_0_15px_rgba(0,240,255,0.15)]',
};

function ToastItem({ toast }) {
  const removeToast = useToastStore((s) => s.removeToast);
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    if (toast.duration <= 0) return;
    const interval = 50;
    const step = (interval / toast.duration) * 100;
    const timer = setInterval(() => {
      setProgress((prev) => Math.max(0, prev - step));
    }, interval);
    return () => clearInterval(timer);
  }, [toast.duration]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 60, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 60, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
      className={`relative overflow-hidden bg-surface/95 backdrop-blur-xl border border-border ${borderMap[toast.type]} border-l-4 rounded-lg p-4 min-w-[320px] max-w-[420px] ${glowMap[toast.type]}`}
    >
      <div className="flex items-start space-x-3">
        <div className="shrink-0 mt-0.5">{iconMap[toast.type]}</div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-bold text-textMain tracking-wide">{toast.title}</p>
          <p className="text-xs text-textMuted mt-0.5 font-mono">{toast.message}</p>
        </div>
        <button
          onClick={() => removeToast(toast.id)}
          className="shrink-0 text-textMuted hover:text-textMain transition-colors"
        >
          <X size={14} />
        </button>
      </div>
      {/* Progress bar */}
      {toast.duration > 0 && (
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-border">
          <motion.div
            className={`h-full ${toast.type === 'success' ? 'bg-success' : toast.type === 'error' ? 'bg-error' : toast.type === 'warning' ? 'bg-warning' : 'bg-primary'}`}
            style={{ width: `${progress}%` }}
            transition={{ ease: 'linear' }}
          />
        </div>
      )}
    </motion.div>
  );
}

export function ToastContainer() {
  const toasts = useToastStore((s) => s.toasts);

  return (
    <div className="fixed top-4 right-4 z-[200] flex flex-col space-y-3 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <ToastItem toast={toast} />
          </div>
        ))}
      </AnimatePresence>
    </div>
  );
}
