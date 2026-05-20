import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Server, AlertTriangle, Users, LogOut, Activity, Flame, MapPin, Globe, Wrench, ShieldCheck, Network, ChevronLeft, ChevronRight, Database } from 'lucide-react';
import useAuthStore from '../../store/authStore';
import { cn } from '../ui/Card';

export function Sidebar({ isOpen, setIsOpen }) {
  const { user, logout } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/devices', icon: Server, label: 'Devices' },
    { to: '/topology', icon: Network, label: 'Topology' },
    { to: '/alerts', icon: AlertTriangle, label: 'Alerts' },
    { to: '/incidents', icon: Flame, label: 'Incidents' },
    { to: '/technicians', icon: Users, label: 'Operatives' },
    { to: '/locations', icon: MapPin, label: 'Facilities' },
    { to: '/vendors', icon: Globe, label: 'Supply Chain' },
    { to: '/maintenance', icon: Wrench, label: 'Maintenance' },
    { to: '/database', icon: Database, label: 'Database Explorer' },
    { to: '/audit-logs', icon: ShieldCheck, label: 'Audit Log' },
  ];

  const sidebarWidth = collapsed ? 'w-[68px]' : 'w-64';

  return (
    <aside className={cn(
      "fixed md:static inset-y-0 left-0 bg-surface/95 backdrop-blur-xl border-r border-border flex flex-col z-40 transition-all duration-300 ease-in-out",
      sidebarWidth,
      isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
    )}>
      {/* Logo */}
      <div className={cn("border-b border-border flex items-center shrink-0 transition-all", collapsed ? "p-3 justify-center" : "px-5 py-4 justify-between")}>
        <div className="flex items-center space-x-2.5 min-w-0">
          <div className="w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/30 shadow-[0_0_15px_rgba(0,240,255,0.15)] shrink-0">
            <Activity size={18} className="text-primary" />
          </div>
          {!collapsed && (
            <span className="text-lg font-bold tracking-wider text-textMain truncate">
              Tele<span className="text-primary">Track</span>
            </span>
          )}
        </div>
        {/* Collapse button — desktop only */}
        <button onClick={() => setCollapsed(!collapsed)}
          className="hidden md:flex items-center justify-center w-7 h-7 rounded-lg text-textMuted hover:text-primary hover:bg-primary/10 transition-all shrink-0">
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto custom-scrollbar">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={() => setIsOpen && setIsOpen(false)}
            title={collapsed ? item.label : undefined}
            className={({ isActive }) => cn(
              "flex items-center rounded-lg transition-all duration-200 group relative",
              collapsed ? "justify-center p-3" : "space-x-3 px-3 py-2.5",
              isActive
                ? "bg-primary/10 text-primary"
                : "text-textMuted hover:bg-surfaceHighlight hover:text-textMain"
            )}
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <div className={cn(
                    "absolute left-0 top-1/2 -translate-y-1/2 w-[3px] rounded-r-full bg-primary shadow-[0_0_8px_rgba(0,240,255,0.6)]",
                    collapsed ? "h-6" : "h-5"
                  )} />
                )}
                <item.icon size={18} className={cn("shrink-0", isActive && "drop-shadow-[0_0_4px_rgba(0,240,255,0.5)]")} />
                {!collapsed && <span className="text-sm font-medium truncate">{item.label}</span>}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className={cn("border-t border-border shrink-0", collapsed ? "p-2" : "p-3")}>
        {!collapsed && (
          <div className="flex items-center space-x-2.5 px-2 py-2 mb-2 rounded-lg bg-surfaceHighlight/50">
            <div className="w-8 h-8 rounded-full bg-accent/20 border border-accent/40 flex items-center justify-center text-accent text-xs font-bold shrink-0">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-textMain truncate">{user?.full_name}</p>
              <p className="text-[10px] text-textMuted truncate font-mono">{user?.roles?.[0]?.display_name || 'Operator'}</p>
            </div>
          </div>
        )}
        <button onClick={logout} title="Logout"
          className={cn(
            "flex items-center text-error/70 hover:text-error hover:bg-error/10 rounded-lg transition-colors",
            collapsed ? "justify-center p-3 w-full" : "space-x-2.5 px-3 py-2 w-full"
          )}>
          <LogOut size={16} />
          {!collapsed && <span className="text-sm font-medium">Logout</span>}
        </button>
      </div>
    </aside>
  );
}
