import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, Settings, Command, LogOut, User, Sun, Moon, Menu } from 'lucide-react';
import { Button } from '../ui/Button';
import { notificationsApi, searchApi } from '../../api';
import useAuthStore from '../../store/authStore';
import useThemeStore from '../../store/themeStore';
import { format } from 'date-fns';

export function Topbar({ toggleSidebar }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  
  const [showSettings, setShowSettings] = useState(false);
  
  const { logout, user } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();
  const navigate = useNavigate();
  
  const searchRef = useRef(null);
  const notifRef = useRef(null);
  const settingsRef = useRef(null);

  useEffect(() => {
    const fetchNotifs = async () => {
      try {
        const res = await notificationsApi.getNotifications({ unread: true, limit: 5 });
        if (res.success && res.data) {
          setNotifications(res.data);
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchNotifs();

    // Listen for real-time notifications via WebSocket
    const handleNewNotif = (e) => {
      setNotifications(prev => [e.detail, ...prev].slice(0, 10));
    };
    window.addEventListener('new_notification', handleNewNotif);
    return () => window.removeEventListener('new_notification', handleNewNotif);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) setShowSearch(false);
      if (notifRef.current && !notifRef.current.contains(event.target)) setShowNotifications(false);
      if (settingsRef.current && !settingsRef.current.contains(event.target)) setShowSettings(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (searchQuery.length >= 2) {
        try {
          const res = await searchApi.globalSearch(searchQuery);
          if (res.success) setSearchResults(res.data);
        } catch (e) {
          console.error(e);
        }
      } else {
        setSearchResults(null);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleMarkRead = async (id) => {
    try {
      await notificationsApi.markRead(id);
      setNotifications(prev => prev.filter(n => n.id !== id));
    } catch (e) {
      console.error(e);
    }
  };

  const handleResultClick = (category, item) => {
    setShowSearch(false);
    setSearchQuery('');
    switch(category.toLowerCase()) {
      case 'devices': navigate('/devices'); break;
      case 'alerts': navigate('/alerts'); break;
      case 'technicians': navigate('/technicians'); break;
      case 'locations': navigate('/locations'); break;
      default: break;
    }
  };

  return (
    <header className="h-16 border-b border-border bg-surface/80 backdrop-blur-md flex items-center justify-between px-4 sm:px-6 sticky top-0 z-50 transition-colors duration-300">
      
      <div className="flex items-center flex-1">
        {/* Mobile Sidebar Toggle */}
        <button 
          onClick={toggleSidebar}
          className="md:hidden mr-3 p-2 text-textMuted hover:text-primary transition-colors"
        >
          <Menu size={20} />
        </button>

        {/* Global Search Bar */}
        <div className="flex-1 max-w-xl" ref={searchRef}>
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-textMuted group-focus-within:text-primary transition-colors">
              <Search size={18} />
            </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setShowSearch(true)}
            className="w-full bg-surfaceHighlight border border-border rounded-lg py-2 pl-10 pr-12 text-textMain focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/50 transition-all font-mono text-sm placeholder-textMuted/60"
            placeholder="Search network, devices, or alerts..."
          />
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <kbd className="hidden sm:inline-flex items-center space-x-1 bg-surface border border-border rounded px-1.5 py-0.5 text-[10px] font-mono text-textMuted">
              <Command size={10} />
              <span>K</span>
            </kbd>
          </div>
          
          {/* Search Results Dropdown */}
          {showSearch && searchQuery.length >= 2 && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-surfaceHighlight border border-primary/30 rounded-lg shadow-[0_10px_30px_rgba(0,0,0,0.8)] backdrop-blur-xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200 z-50">
              {searchResults ? (
                <div className="max-h-96 overflow-y-auto custom-scrollbar p-2">
                  {Object.entries(searchResults).map(([category, items]) => {
                    if (!items || items.length === 0) return null;
                    return (
                      <div key={category} className="mb-4 last:mb-0">
                        <div className="px-3 py-1.5 text-xs font-bold text-primary uppercase tracking-widest bg-primary/5 rounded">
                          {category}
                        </div>
                        <div className="mt-1">
                          {items.map((item, idx) => (
                            <div 
                              key={idx} 
                              onClick={() => handleResultClick(category, item)}
                              className="px-3 py-2 hover:bg-primary/10 rounded cursor-pointer transition-colors group"
                            >
                              <p className="text-sm text-textMain group-hover:text-primary">{item.name || item.type}</p>
                              <p className="text-xs text-textMuted font-mono truncate">{item.ip || item.severity || item.city || item.status}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                  {Object.values(searchResults).every(arr => arr.length === 0) && (
                    <div className="p-4 text-center text-textMuted font-mono text-sm">NO MATCHES FOUND</div>
                  )}
                </div>
              ) : (
                <div className="p-4 text-center text-textMuted flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                  <span className="font-mono text-sm">SCANNING...</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center space-x-3 ml-6">
        
        {/* Theme Toggle */}
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={toggleTheme}
          className="p-2 w-10 h-10 rounded-full bg-surfaceHighlight/50 border border-transparent hover:border-primary/50 group"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? (
            <Sun size={18} className="group-hover:text-warning transition-colors" />
          ) : (
            <Moon size={18} className="group-hover:text-primary transition-colors" />
          )}
        </Button>

        {/* Notifications Popover */}
        <div className="relative" ref={notifRef}>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setShowNotifications(!showNotifications)}
            className={`relative p-2 w-10 h-10 rounded-full bg-surfaceHighlight/50 border ${showNotifications ? 'border-primary' : 'border-transparent'} hover:border-primary/50 group`}
          >
            <Bell size={18} className="group-hover:text-primary transition-colors" />
            {notifications.length > 0 && (
              <span className="absolute top-1.5 right-1.5 flex items-center justify-center min-w-[16px] h-4 px-1 bg-error rounded-full text-[9px] font-bold text-white shadow-[0_0_5px_rgba(255,0,60,0.8)]">
                {notifications.length > 9 ? '9+' : notifications.length}
              </span>
            )}
          </Button>

          {showNotifications && (
            <div className="absolute top-full right-0 mt-2 w-80 bg-surface border border-border rounded-lg shadow-[0_10px_40px_rgba(0,0,0,0.9)] overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200 z-50">
              <div className="p-3 border-b border-border bg-surfaceHighlight flex items-center justify-between">
                <span className="font-bold text-sm text-textMain tracking-wider">SYSTEM ALERTS</span>
                {notifications.length > 0 && <span className="bg-error/20 text-error text-xs px-2 py-0.5 rounded font-mono">{notifications.length} NEW</span>}
              </div>
              <div className="max-h-80 overflow-y-auto custom-scrollbar">
                {notifications.length === 0 ? (
                  <div className="p-6 text-center text-textMuted font-mono text-sm">NO NEW ALERTS</div>
                ) : (
                  <div className="divide-y divide-border/50">
                    {notifications.map(n => (
                      <div key={n.id} className="p-3 hover:bg-surfaceHighlight/50 transition-colors group cursor-pointer" onClick={() => handleMarkRead(n.id)}>
                        <div className="flex items-start justify-between">
                          <p className="text-sm font-medium text-textMain group-hover:text-primary transition-colors pr-2">{n.message || n.title}</p>
                          <div className="w-2 h-2 bg-primary rounded-full mt-1.5 shrink-0 shadow-[0_0_5px_var(--neon-glow)]"></div>
                        </div>
                        <p className="text-xs text-textMuted font-mono mt-1">{n.created_at ? format(new Date(n.created_at), 'MMM dd HH:mm') : ''}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Settings Popover */}
        <div className="relative" ref={settingsRef}>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 w-10 h-10 rounded-full bg-surfaceHighlight/50 border ${showSettings ? 'border-primary' : 'border-transparent'} hover:border-primary/50 group overflow-hidden`}
          >
            <Settings size={18} className="group-hover:text-primary transition-colors" />
          </Button>

          {showSettings && (
            <div className="absolute top-full right-0 mt-2 w-48 bg-surface border border-border rounded-lg shadow-[0_10px_40px_rgba(0,0,0,0.9)] overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200 z-50">
              <div className="p-3 border-b border-border bg-surfaceHighlight">
                <p className="text-sm font-bold text-textMain truncate">{user?.full_name}</p>
                <p className="text-xs text-textMuted truncate font-mono mt-0.5">{user?.roles?.[0]?.display_name}</p>
              </div>
              <div className="p-1">
                <button className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-textMuted hover:text-textMain hover:bg-surfaceHighlight rounded transition-colors">
                  <User size={14} />
                  <span>Profile Settings</span>
                </button>
                <button 
                  onClick={toggleTheme}
                  className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-textMuted hover:text-textMain hover:bg-surfaceHighlight rounded transition-colors"
                >
                  {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
                  <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
                </button>
                <div className="h-px bg-border my-1"></div>
                <button onClick={logout} className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-error hover:bg-error/10 rounded transition-colors">
                  <LogOut size={14} />
                  <span>Terminate Session</span>
                </button>
              </div>
            </div>
          )}
        </div>

      </div>
    </header>
  );
}
