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
      className="space-y-6 h-full flex flex-col"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div>
        <h1 className="text-3xl font-bold text-textMain tracking-wide">INFRASTRUCTURE <span className="text-primary neon-text">TOPOLOGY</span></h1>
        <p className="text-textMuted mt-1 font-mono text-sm uppercase">Spatial Asset Mapping</p>
      </div>

      <Card className="flex-1 bg-surfaceHighlight/10 border-dashed border-2 border-border relative overflow-hidden flex items-center justify-center">
        {loading ? (
          <div className="animate-pulse text-primary font-mono text-sm">INITIALIZING SCAN...</div>
        ) : (
          <div className="relative w-full h-full p-20 flex flex-wrap justify-center items-center gap-16">
            {/* Core Node Simulation */}
            <motion.div 
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-24 h-24 rounded-full bg-primary/10 border-2 border-primary flex items-center justify-center shadow-[0_0_30px_rgba(0,240,255,0.3)] z-20"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ repeat: Infinity, duration: 4 }}
            >
              <Network size={40} className="text-primary" />
              <div className="absolute -bottom-8 text-xs font-mono text-primary font-bold">CORE-FABRIC-01</div>
            </motion.div>

            {/* Device Nodes */}
            {devices.map((device, i) => {
              const angle = (i / devices.length) * 2 * Math.PI;
              const radius = 250;
              const x = Math.cos(angle) * radius;
              const y = Math.sin(angle) * radius;

              return (
                <motion.div
                  key={device.id}
                  className="absolute z-10"
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1, x, y }}
                  transition={{ delay: i * 0.1, type: 'spring' }}
                >
                  <div className={`relative group flex flex-col items-center justify-center w-16 h-16 rounded-lg bg-surface border transition-all hover:scale-110 ${device.status === 'online' ? 'border-primary/50' : 'border-error/50'}`}>
                    <div className={`absolute inset-0 rounded-lg blur-sm opacity-20 group-hover:opacity-40 transition-opacity ${device.status === 'online' ? 'bg-primary' : 'bg-error'}`}></div>
                    <div className={device.status === 'online' ? 'text-primary' : 'text-error'}>
                      {getIcon(device.device_type)}
                    </div>
                    
                    {/* Tooltip */}
                    <div className="absolute top-full mt-2 hidden group-hover:block z-30 bg-surfaceHighlight border border-border p-2 rounded shadow-xl min-w-[150px]">
                      <p className="text-xs font-bold text-textMain">{device.device_name}</p>
                      <p className="text-[10px] font-mono text-textMuted">{device.ip_address}</p>
                      <p className={`text-[10px] font-mono uppercase mt-1 ${device.status === 'online' ? 'text-success' : 'text-error'}`}>{device.status}</p>
                    </div>

                    {/* Connection Line Simulation (SVG) */}
                    <svg className="absolute top-1/2 left-1/2 w-[400px] h-[400px] pointer-events-none -z-10 overflow-visible" style={{ transform: `translate(-50%, -50%) rotate(${angle}rad)` }}>
                      <line 
                        x1="0" y1="0" x2="-200" y2="0" 
                        stroke="currentColor" 
                        strokeWidth="1" 
                        strokeDasharray="4 4"
                        className={`${device.status === 'online' ? 'text-primary/20' : 'text-error/20'}`}
                      />
                    </svg>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </Card>
    </motion.div>
  );
}
