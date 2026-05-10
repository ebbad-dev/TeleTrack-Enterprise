import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Shield, Lock, ChevronRight, Fingerprint } from 'lucide-react';
import useAuthStore from '../store/authStore';

// Cyberpunk particles component
const Particles = () => {
  const [dots, setDots] = useState([]);
  
  useEffect(() => {
    // Generate random particles
    const generated = Array.from({ length: 40 }).map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 3 + 1,
      duration: Math.random() * 20 + 10,
      delay: Math.random() * 5
    }));
    setDots(generated);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
      {dots.map(dot => (
        <motion.div
          key={dot.id}
          className="absolute bg-primary rounded-full shadow-[0_0_10px_rgba(0,240,255,1)]"
          style={{ width: dot.size, height: dot.size, left: `${dot.x}%`, top: `${dot.y}%` }}
          animate={{
            y: [0, -1000],
            opacity: [0, 1, 0]
          }}
          transition={{
            duration: dot.duration,
            repeat: Infinity,
            delay: dot.delay,
            ease: "linear"
          }}
        />
      ))}
    </div>
  );
};

export function LoginPage() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('TeleTrack@2026');
  const [error, setError] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [terminalText, setTerminalText] = useState('AWAITING CREDENTIALS...');
  
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsScanning(true);
    setTerminalText('INITIATING BIOMETRIC SCAN...');

    // Fake scanning delay for visual effect
    setTimeout(() => {
      setTerminalText('AUTHENTICATING WITH MAINFRAME...');
    }, 800);

    setTimeout(async () => {
      const success = await login({ username, password });
      if (success) {
        setTerminalText('ACCESS GRANTED. DECRYPTING PAYLOAD...');
        setTimeout(() => navigate('/'), 600);
      } else {
        setError('AUTHORIZATION DENIED. INVALID CREDENTIALS.');
        setTerminalText('ACCESS DENIED.');
        setIsScanning(false);
      }
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center relative overflow-hidden font-sans">
      
      {/* Background Effects */}
      <div className="absolute inset-0 bg-cyber-grid bg-[length:30px_30px] opacity-10"></div>
      <div className="absolute inset-0 bg-radial-gradient"></div>
      <Particles />

      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-md relative z-10"
      >
        <div className="glass-panel p-8 relative overflow-hidden">
          
          {/* Scanning Line Effect */}
          <AnimatePresence>
            {isScanning && (
              <motion.div 
                initial={{ top: '-10%' }}
                animate={{ top: '110%' }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                className="absolute left-0 right-0 h-1 bg-primary/80 shadow-[0_0_20px_rgba(0,240,255,1)] z-50 pointer-events-none"
              />
            )}
          </AnimatePresence>

          <div className="text-center mb-10 relative">
            <div className="absolute inset-0 blur-2xl bg-primary/20 rounded-full scale-150"></div>
            <Activity className="mx-auto h-14 w-14 text-primary neon-text mb-4 relative z-10" />
            <h1 className="text-4xl font-bold text-textMain tracking-widest uppercase relative z-10">TeleTrack</h1>
            <p className="text-primary/80 font-mono text-sm tracking-[0.3em] mt-2 relative z-10">ENTERPRISE SYSTEM</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6 relative z-10">
            <div className="space-y-4">
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Shield className="h-5 w-5 text-textMuted group-focus-within:text-primary transition-colors" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="block w-full pl-10 bg-surface/50 border border-border rounded text-textMain focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm py-3 transition-all placeholder-textMuted/50 font-mono neon-border hover:border-primary/50"
                  placeholder="OPERATOR ID"
                  disabled={isScanning}
                />
              </div>

              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-textMuted group-focus-within:text-primary transition-colors" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 bg-surface/50 border border-border rounded text-textMain focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm py-3 transition-all placeholder-textMuted/50 font-mono neon-border hover:border-primary/50"
                  placeholder="SECURITY KEY"
                  disabled={isScanning}
                />
              </div>
            </div>

            {error && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-error text-xs font-mono bg-error/10 p-2 border border-error/30 rounded"
              >
                {error}
              </motion.div>
            )}

            <button
              type="submit"
              disabled={isScanning}
              className="w-full flex items-center justify-center py-3 px-4 border border-transparent rounded text-sm font-bold text-background bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary focus:ring-offset-background transition-all uppercase tracking-widest shadow-[0_0_15px_rgba(0,240,255,0.4)] hover:shadow-[0_0_25px_rgba(0,240,255,0.6)] disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              {isScanning ? (
                <>
                  <Fingerprint className="animate-pulse mr-2" size={18} />
                  VERIFYING...
                </>
              ) : (
                <>
                  ACCESS SYSTEM
                  <ChevronRight className="ml-2 group-hover:translate-x-1 transition-transform" size={18} />
                </>
              )}
            </button>
          </form>

          {/* Terminal Output Simulation */}
          <div className="mt-8 pt-4 border-t border-border/50">
            <div className="flex items-center space-x-2 text-[10px] font-mono text-primary/70">
              <span className="animate-pulse">_</span>
              <span>{terminalText}</span>
            </div>
          </div>

        </div>
      </motion.div>
    </div>
  );
}
