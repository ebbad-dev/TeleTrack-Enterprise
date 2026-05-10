import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Network, Server, HardDrive, Shield, Router } from 'lucide-react';
import { devicesApi } from '../api';
import { Card } from '../components/ui/Card';

export function TopologyPage() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const res = await devicesApi.getDevices();
        if (res.success) setDevices(res.data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchDevices();
  }, []);

  const getIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'router': return <Router size={24} />;
      case 'switch': return <Network size={24} />;
      case 'firewall': return <Shield size={24} />;
      case 'storage': return <HardDrive size={24} />;
      default: return <Server size={24} />;
    }
  };

  return (
    <motion.div 
      className="h-full flex flex-col -m-6" # Use negative margins to bleed into the parent container
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="p-6 pb-2 shrink-0">
        <h1 className="text-3xl font-bold text-textMain tracking-wide">INFRASTRUCTURE <span className="text-primary neon-text">TOPOLOGY</span></h1>
        <p className="text-textMuted mt-1 font-mono text-sm uppercase">Spatial Asset Mapping</p>
      </div>

      <div className="flex-1 bg-surfaceHighlight/5 border-t border-border relative overflow-hidden">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center animate-pulse text-primary font-mono text-sm">INITIALIZING SCAN...</div>
        ) : (
          <div className="w-full h-full relative overflow-hidden bg-cyber-grid bg-[length:50px_50px] opacity-20">
            <div className="absolute inset-0 flex items-center justify-center p-20">
              {/* Core Node */}
              <motion.div 
                className="w-32 h-32 rounded-full bg-primary/10 border-2 border-primary flex items-center justify-center shadow-[0_0_50px_rgba(0,240,255,0.4)] z-20 relative"
                animate={{ scale: [1, 1.05, 1], boxShadow: ["0 0 30px rgba(0,240,255,0.3)", "0 0 60px rgba(0,240,255,0.6)", "0 0 30px rgba(0,240,255,0.3)"] }}
                transition={{ repeat: Infinity, duration: 4 }}
              >
                <Network size={56} className="text-primary" />
                <div className="absolute -bottom-10 whitespace-nowrap text-xs font-mono text-primary font-bold tracking-widest bg-background/80 px-2 py-1 rounded border border-primary/30">CORE-FABRIC-01</div>
              </motion.div>

              {/* Device Nodes */}
              {devices.map((device, i) => {
                const angle = (i / devices.length) * 2 * Math.PI;
                # Dynamic radius based on screen size and device count
                const radius = Math.min(window.innerWidth, window.innerHeight) * 0.35 + (i * 2);
                const x = Math.cos(angle) * radius;
                const y = Math.sin(angle) * radius;

                return (
                  <motion.div
                    key={device.id}
                    className="absolute z-10"
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1, x, y }}
                    transition={{ delay: i * 0.05, type: 'spring', damping: 12 }}
                  >
                    <div className={`relative group flex flex-col items-center justify-center w-20 h-20 rounded-xl bg-surface/90 backdrop-blur-sm border-2 transition-all hover:scale-125 cursor-pointer shadow-lg ${device.status === 'online' ? 'border-primary/50 hover:border-primary shadow-primary/10' : 'border-error/50 hover:border-error shadow-error/10'}`}>
                      <div className={`absolute inset-0 rounded-xl blur-md opacity-20 group-hover:opacity-60 transition-opacity ${device.status === 'online' ? 'bg-primary' : 'bg-error'}`}></div>
                      <div className={device.status === 'online' ? 'text-primary' : 'text-error'}>
                        {getIcon(device.device_type)}
                      </div>
                      
                      {/* Condensed Label */}
                      <div className="absolute -bottom-6 opacity-60 group-hover:opacity-100 transition-opacity text-[9px] font-mono text-textMuted uppercase truncate max-w-[80px]">
                        {device.device_name}
                      </div>

                      {/* Tooltip Card */}
                      <div className="absolute bottom-full mb-4 hidden group-hover:block z-40 bg-surfaceHighlight/95 backdrop-blur-xl border border-primary/50 p-4 rounded-lg shadow-2xl min-w-[200px] border-b-4 border-b-primary animate-in fade-in zoom-in duration-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${device.status === 'online' ? 'bg-success/20 text-success' : 'bg-error/20 text-error'}`}>
                            {device.status}
                          </span>
                          <span className="text-[10px] font-mono text-textMuted">{device.device_type}</span>
                        </div>
                        <h4 className="text-sm font-bold text-textMain mb-1">{device.device_name}</h4>
                        <div className="space-y-1 border-t border-border mt-2 pt-2">
                          <div className="flex justify-between text-[10px]">
                            <span className="text-textMuted">IP ADDRESS</span>
                            <span className="font-mono text-primary">{device.ip_address}</span>
                          </div>
                          <div className="flex justify-between text-[10px]">
                            <span className="text-textMuted">MODEL</span>
                            <span className="font-mono">{device.model || 'GENERIC-V4'}</span>
                          </div>
                        </div>
                      </div>

                      {/* Animated Connection Path */}
                      <svg className="absolute top-1/2 left-1/2 w-[800px] h-[800px] pointer-events-none -z-10 overflow-visible" style={{ transform: `translate(-50%, -50%) rotate(${angle}rad)` }}>
                        <line 
                          x1="0" y1="0" x2={-radius} y2="0" 
                          stroke="currentColor" 
                          strokeWidth="1.5" 
                          strokeDasharray="8 4"
                          className={`${device.status === 'online' ? 'text-primary/30' : 'text-error/30'}`}
                        />
                        {device.status === 'online' && (
                          <motion.circle
                            r="3"
                            fill="#00f0ff"
                            animate={{ cx: [0, -radius] }}
                            transition={{ repeat: Infinity, duration: 2, ease: "linear", delay: i * 0.2 }}
                          />
                        )}
                      </svg>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
