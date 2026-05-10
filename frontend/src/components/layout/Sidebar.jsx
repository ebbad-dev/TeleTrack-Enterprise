import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Server, AlertTriangle, Users, Settings, LogOut, Activity, Flame, MapPin, Globe, Wrench, ShieldCheck } from 'lucide-react';
import useAuthStore from '../../store/authStore';
import { cn } from '../ui/Card';

export function Sidebar() {
  const { user, logout } = useAuthStore();

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/devices', icon: Server, label: 'Devices' },
    { to: '/alerts', icon: AlertTriangle, label: 'Alerts' },
    { to: '/incidents', icon: Flame, label: 'Incidents' },
    { to: '/technicians', icon: Users, label: 'Operatives' },
    { to: '/locations', icon: MapPin, label: 'Facilities' },
    { to: '/vendors', icon: Globe, label: 'Supply Chain' },
    { to: '/maintenance', icon: Wrench, label: 'Maintenance' },
    { to: '/audit-logs', icon: ShieldCheck, label: 'Security Log' },
  ];

  return (
    <aside className="w-64 h-screen bg-surface border-r border-border flex flex-col relative z-20">
      <div className="p-6 border-b border-border flex items-center space-x-3">
        <div className="w-8 h-8 rounded bg-primary/20 flex items-center justify-center border border-primary/50 shadow-[0_0_15px_rgba(0,240,255,0.3)]">
          <Activity size={18} className="text-primary" />
        </div>
        <span className="text-xl font-bold tracking-wider text-textMain neon-text">TeleTrack</span>
      </div>

      <nav className="flex-1 py-6 px-4 space-y-2 overflow-y-auto custom-scrollbar">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => cn(
              "flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-300",
              isActive 
                ? "bg-primary/10 text-primary border border-primary/30 shadow-[inset_4px_0_0_rgba(0,240,255,1)]" 
                : "text-textMuted hover:bg-surfaceHighlight hover:text-textMain"
            )}
          >
            <item.icon size={20} />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="flex items-center space-x-3 px-4 py-3 mb-2 rounded-lg bg-surfaceHighlight/50">
          <div className="w-8 h-8 rounded-full bg-accent/20 border border-accent flex items-center justify-center text-accent font-bold">
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-textMain truncate">{user?.full_name}</p>
            <p className="text-xs text-textMuted truncate">{user?.roles?.[0]?.display_name}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center space-x-3 px-4 py-2 text-error hover:bg-error/10 rounded-lg transition-colors"
        >
          <LogOut size={18} />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </aside>
  );
}
