import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save } from 'lucide-react';
import { Card } from './Card';
import { Button } from './Button';

export function DataModal({ isOpen, onClose, onSave, title, fields, initialData, isSaving }) {
  const [formData, setFormData] = React.useState({});

  React.useEffect(() => {
    if (isOpen) {
      setFormData(initialData || {});
    }
  }, [isOpen, initialData]);

  const handleChange = (e, field) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative w-full max-w-lg"
          >
            <Card className="border-primary/50 shadow-[0_0_30px_rgba(0,240,255,0.15)] p-0 overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-border bg-surfaceHighlight">
                <h2 className="text-lg font-bold text-textMain tracking-widest">{title}</h2>
                <button onClick={onClose} className="text-textMuted hover:text-error transition-colors">
                  <X size={20} />
                </button>
              </div>
              
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                {fields.map((field) => (
                  <div key={field.name} className="space-y-1">
                    <label className="text-xs font-mono text-textMuted uppercase tracking-wider">
                      {field.label}
                      {field.required && <span className="text-error ml-1">*</span>}
                    </label>
                    {field.type === 'select' ? (
                      <select
                        value={formData[field.name] || ''}
                        onChange={(e) => handleChange(e, field.name)}
                        required={field.required}
                        className="w-full bg-surface border border-border rounded p-2 text-textMain text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all font-mono"
                      >
                        <option value="" disabled>Select {field.label}</option>
                        {field.options?.map(opt => (
                          <option key={opt.value} value={opt.value}>{opt.label}</option>
                        ))}
                      </select>
                    ) : field.type === 'textarea' ? (
                      <textarea
                        value={formData[field.name] || ''}
                        onChange={(e) => handleChange(e, field.name)}
                        required={field.required}
                        rows={3}
                        className="w-full bg-surface border border-border rounded p-2 text-textMain text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all font-mono custom-scrollbar"
                      />
                    ) : (
                      <input
                        type={field.type || 'text'}
                        value={formData[field.name] || ''}
                        onChange={(e) => handleChange(e, field.name)}
                        required={field.required}
                        className="w-full bg-surface border border-border rounded p-2 text-textMain text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all font-mono"
                      />
                    )}
                  </div>
                ))}

                <div className="pt-4 flex justify-end space-x-3">
                  <Button variant="ghost" type="button" onClick={onClose} disabled={isSaving}>
                    CANCEL
                  </Button>
                  <Button variant="primary" type="submit" disabled={isSaving}>
                    {isSaving ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin"></div>
                        <span>PROCESSING</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <Save size={16} />
                        <span>COMMIT CHANGES</span>
                      </div>
                    )}
                  </Button>
                </div>
              </form>
            </Card>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
