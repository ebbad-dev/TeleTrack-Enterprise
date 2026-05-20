import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Shield, Lock, ChevronRight, Eye, EyeOff, Wifi, Server, Cpu, Zap } from 'lucide-react';
import useAuthStore from '../store/authStore';

/* ── Particle Canvas Background ──────────────────────────── */
function ParticleCanvas() {
  const canvasRef = useRef(null);
  const animRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let w, h;

    const resize = () => {
      w = canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      h = canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    resize();
    window.addEventListener('resize', resize);

    // Create particles
    const count = Math.min(80, Math.floor((canvas.offsetWidth * canvas.offsetHeight) / 12000));
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * canvas.offsetWidth,
        y: Math.random() * canvas.offsetHeight,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 1.5 + 0.5,
        opacity: Math.random() * 0.5 + 0.1,
      });
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            const alpha = (1 - dist / 120) * 0.12;
            ctx.beginPath();
            ctx.strokeStyle = `rgba(0, 240, 255, ${alpha})`;
            ctx.lineWidth = 0.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw & update particles
      particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 240, 255, ${p.opacity})`;
        ctx.fill();

        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > canvas.offsetWidth) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.offsetHeight) p.vy *= -1;
      });

      animRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resize);
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ opacity: 0.6 }}
    />
  );
}

/* ── Animated grid background ─────────────────────────── */
function GridBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <div className="absolute inset-0 bg-cyber-grid bg-[length:40px_40px] opacity-[0.04]" />
      <div className="absolute inset-0 bg-radial-gradient" />
      {/* Floating orbs */}
      <motion.div className="absolute w-[500px] h-[500px] rounded-full top-[-10%] left-[-10%]"
        style={{ background: 'radial-gradient(circle, rgba(0,240,255,0.06) 0%, transparent 70%)' }}
        animate={{ scale: [1, 1.2, 1], x: [0, 30, 0], y: [0, 20, 0] }}
        transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }} />
      <motion.div className="absolute w-[400px] h-[400px] rounded-full bottom-[-5%] right-[-5%]"
        style={{ background: 'radial-gradient(circle, rgba(124,58,237,0.05) 0%, transparent 70%)' }}
        animate={{ scale: [1.1, 1, 1.1], x: [0, -20, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }} />
      <motion.div className="absolute w-[300px] h-[300px] rounded-full top-[40%] right-[20%]"
        style={{ background: 'radial-gradient(circle, rgba(0,255,136,0.03) 0%, transparent 70%)' }}
        animate={{ scale: [1, 1.3, 1], y: [0, -30, 0] }}
        transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }} />
    </div>
  );
}

/* ── Typewriter status text ───────────────────────────────── */
function TypewriterText({ text }) {
  const [displayed, setDisplayed] = useState('');
  useEffect(() => {
    setDisplayed('');
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayed(text.slice(0, i + 1));
        i++;
      } else {
        clearInterval(timer);
      }
    }, 40);
    return () => clearInterval(timer);
  }, [text]);

  return (
    <span>
      {displayed}
      <span className="animate-pulse">_</span>
    </span>
  );
}

/* ── Left panel telemetry visualization ───────────────── */
function TelemetryPanel() {
  const [metrics] = useState(() =>
    Array.from({ length: 6 }, (_, i) => ({
      id: i, label: ['NODES', 'UPTIME', 'LATENCY', 'TRAFFIC', 'CPU', 'MEMORY'][i],
      value: ['2,847', '99.97%', '12ms', '48.2 Gbps', '34%', '61%'][i],
      icon: [Server, Wifi, Activity, Zap, Cpu, Server][i],
    }))
  );

  return (
    <div className="hidden lg:flex flex-col justify-center items-center flex-1 relative p-12">
      <ParticleCanvas />
      <GridBackground />
      <div className="relative z-10 max-w-md w-full space-y-8">
        {/* Logo */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }} className="text-center">
          <motion.div
            className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-primary/10 border border-primary/30 mb-6"
            animate={{ boxShadow: ['0 0 20px rgba(0,240,255,0.1)', '0 0 40px rgba(0,240,255,0.2)', '0 0 20px rgba(0,240,255,0.1)'] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          >
            <Activity size={40} className="text-primary" />
          </motion.div>
          <h1 className="text-5xl font-black text-textMain tracking-tight">
            Tele<span className="text-primary neon-text">Track</span>
          </h1>
          <p className="text-textMuted mt-3 text-sm tracking-[0.2em] uppercase font-mono">
            Enterprise Telemetry Platform
          </p>
        </motion.div>

        {/* Live metrics grid */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="grid grid-cols-3 gap-3">
          {metrics.map((m, i) => (
            <motion.div key={m.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8 + i * 0.1 }}
              className="glass-card p-3 text-center group cursor-default">
              <m.icon size={16} className="mx-auto text-primary/60 mb-1.5 group-hover:text-primary transition-colors" />
              <p className="text-lg font-bold text-textMain font-mono">{m.value}</p>
              <p className="text-[9px] text-textMuted uppercase tracking-widest mt-0.5">{m.label}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Decorative data stream line */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.4 }}>
          <svg className="w-full h-6 opacity-30" viewBox="0 0 400 20" preserveAspectRatio="none">
            <line x1="0" y1="10" x2="400" y2="10" stroke="rgba(0,240,255,0.2)" strokeWidth="1" />
            <circle r="3" fill="#00f0ff" opacity="0.8">
              <animateMotion dur="3s" repeatCount="indefinite" path="M0,10 L400,10" />
            </circle>
            <circle r="2" fill="#7c3aed" opacity="0.6">
              <animateMotion dur="4s" repeatCount="indefinite" path="M400,10 L0,10" />
            </circle>
          </svg>
        </motion.div>

        {/* Status bar */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.6 }}
          className="flex items-center justify-center space-x-6 text-[10px] font-mono text-textMuted uppercase tracking-wider">
          <span className="flex items-center"><span className="status-dot status-dot-online mr-2" />Systems Online</span>
          <span>Protocol: TLS 1.3</span>
          <span>Region: Global</span>
        </motion.div>
      </div>
    </div>
  );
}

/* ── Main Login Page ──────────────────────────────────── */
export function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [statusText, setStatusText] = useState('SYSTEM READY');
  const usernameRef = useRef(null);

  const { login } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => { usernameRef.current?.focus(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('All fields are required');
      return;
    }
    setError('');
    setIsLoading(true);
    setStatusText('AUTHENTICATING...');

    try {
      const success = await login({ username: username.trim(), password });
      if (success) {
        setStatusText('ACCESS GRANTED');
        setTimeout(() => navigate('/'), 600);
      } else {
        setError('Invalid credentials. Access denied.');
        setStatusText('ACCESS DENIED');
        setIsLoading(false);
      }
    } catch {
      setError('Authentication service unavailable');
      setStatusText('CONNECTION ERROR');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left — Telemetry Visualization */}
      <TelemetryPanel />

      {/* Right — Login Form */}
      <div className="flex-1 lg:max-w-[520px] flex items-center justify-center relative p-6 sm:p-12">
        <GridBackground />

        {/* Scan line effect during loading */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ top: 0, opacity: 0 }}
              animate={{ top: '100%', opacity: [0, 1, 1, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
              className="absolute left-0 right-0 h-0.5 bg-primary shadow-[0_0_15px_rgba(0,240,255,0.8)] z-50 pointer-events-none"
            />
          )}
        </AnimatePresence>

        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="w-full max-w-sm relative z-10"
        >
          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-primary/10 border border-primary/30 mb-4">
              <Activity size={28} className="text-primary" />
            </div>
            <h1 className="text-3xl font-black text-textMain">
              Tele<span className="text-primary neon-text">Track</span>
            </h1>
            <p className="text-textMuted text-xs tracking-[0.2em] uppercase font-mono mt-1">Enterprise System</p>
          </div>

          {/* Form card */}
          <div className="glass-panel p-8 space-y-6 gradient-border">
            <div>
              <h2 className="text-xl font-bold text-textMain">Sign In</h2>
              <p className="text-textMuted text-sm mt-1">Enter your credentials to access the platform</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Username */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-textMuted uppercase tracking-wider">Operator ID</label>
                <div className="relative group">
                  <Shield size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted group-focus-within:text-primary transition-colors" />
                  <input
                    ref={usernameRef}
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={isLoading}
                    className="w-full pl-10 pr-4 py-3 bg-surface/60 border border-border rounded-lg text-textMain text-sm font-mono
                      focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
                      hover:border-primary/30 transition-all placeholder-textMuted/40 disabled:opacity-50"
                    placeholder="Username or email"
                    autoComplete="username"
                  />
                </div>
              </div>

              {/* Password */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-textMuted uppercase tracking-wider">Access Key</label>
                <div className="relative group">
                  <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted group-focus-within:text-primary transition-colors" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={isLoading}
                    className="w-full pl-10 pr-12 py-3 bg-surface/60 border border-border rounded-lg text-textMain text-sm font-mono
                      focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
                      hover:border-primary/30 transition-all placeholder-textMuted/40 disabled:opacity-50"
                    placeholder="Enter password"
                    autoComplete="current-password"
                  />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} tabIndex={-1}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-textMuted hover:text-primary transition-colors">
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {/* Error */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -5, height: 0 }}
                    animate={{ opacity: 1, y: 0, height: 'auto' }}
                    exit={{ opacity: 0, y: -5, height: 0 }}
                    className="text-error text-xs font-mono bg-error/5 border border-error/20 rounded-lg px-3 py-2.5 flex items-center gap-2"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-error animate-pulse shrink-0" />
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Submit */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center py-3 rounded-lg text-sm font-bold
                  bg-primary text-background hover:brightness-110
                  focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2 focus:ring-offset-background
                  transition-all uppercase tracking-wider
                  shadow-[0_0_20px_rgba(0,240,255,0.2)] hover:shadow-[0_0_30px_rgba(0,240,255,0.35)]
                  disabled:opacity-50 disabled:cursor-not-allowed group btn-ripple"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin mr-2" />
                    Authenticating...
                  </>
                ) : (
                  <>
                    Access System
                    <ChevronRight size={16} className="ml-2 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>

            {/* Footer */}
            <div className="pt-4 border-t border-border/50 flex items-center justify-between">
              <span className="text-[10px] font-mono text-textMuted/60 flex items-center">
                <span className={`status-dot mr-1.5 ${isLoading ? 'status-dot-degraded' : 'status-dot-online'}`} />
                <TypewriterText text={statusText} />
              </span>
              <span className="text-[10px] font-mono text-textMuted/40">v5.0</span>
            </div>
          </div>

          {/* Security badge */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="mt-6 text-center"
          >
            <p className="text-[9px] font-mono text-textMuted/30 uppercase tracking-widest flex items-center justify-center gap-2">
              <Lock size={8} />
              256-bit AES Encrypted • SOC2 Compliant
            </p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
