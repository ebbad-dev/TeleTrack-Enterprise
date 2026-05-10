import React, { useEffect, useState, useRef, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Network, Maximize, Minimize, RefreshCw } from 'lucide-react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import { devicesApi, networkApi } from '../api';
import { extractItems } from '../api/helpers';
import { Card } from '../components/ui/Card';
import useToastStore from '../store/toastStore';

export function TopologyPage() {
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const containerRef = useRef(null);
  const graphRef = useRef();
  const toast = useToastStore;

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch all devices and links
      const [devRes, linkRes] = await Promise.all([
        devicesApi.getDevices({ per_page: 1000 }),
        networkApi.getLinks({ per_page: 1000 })
      ]);
      
      const devicesData = extractItems(devRes);
      const linksData = extractItems(linkRes);

      // Transform for react-force-graph
      const formattedNodes = devicesData.map(d => ({
        id: d.id,
        name: d.device_name,
        type: d.device_type,
        status: d.status,
        ip: d.ip_address,
        val: d.device_type === 'Router' ? 25 : d.device_type === 'Switch' ? 20 : 15,
        color: d.status === 'online' ? '#00f0ff' : d.status === 'degraded' ? '#ffb300' : '#ff003c'
      }));

      // Only include links where both source and target exist in nodes
      const nodeIds = new Set(formattedNodes.map(n => n.id));
      const formattedLinks = linksData
        .filter(l => nodeIds.has(l.source_device_id) && nodeIds.has(l.target_device_id))
        .map(l => ({
          source: l.source_device_id,
          target: l.target_device_id,
          type: l.link_type,
          status: l.status,
          bandwidth: l.bandwidth,
          color: l.status === 'active' ? '#00f0ff' : '#ffb300'
        }));

      setNodes(formattedNodes);
      setLinks(formattedLinks);
      
      // Auto-fit camera after data loads
      setTimeout(() => {
        if (graphRef.current) {
          graphRef.current.zoomToFit(400, 50);
        }
      }, 500);

    } catch (error) {
      console.error('Topology fetch error', error);
      toast.error('Failed to load network topology');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Handle responsive sizing
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, [isFullscreen]);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    setTimeout(() => {
      if (graphRef.current) graphRef.current.zoomToFit(400, 50);
    }, 100);
  };

  const graphData = useMemo(() => ({ nodes, links }), [nodes, links]);

  return (
    <motion.div 
      className={`space-y-6 flex flex-col ${isFullscreen ? 'fixed inset-0 z-50 p-6 bg-background' : 'h-full'}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-3xl font-bold text-textMain tracking-wide">NETWORK <span className="text-primary neon-text">TOPOLOGY</span></h1>
          <p className="text-textMuted mt-1 font-mono text-sm uppercase">Interactive 3D Infrastructure Map</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button 
            onClick={fetchData}
            className="p-2 text-textMuted hover:text-primary transition-colors bg-surfaceHighlight rounded border border-border hover:border-primary/50"
            title="Refresh Topology"
          >
            <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
          </button>
          <button 
            onClick={toggleFullscreen}
            className="p-2 text-textMuted hover:text-primary transition-colors bg-surfaceHighlight rounded border border-border hover:border-primary/50"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize size={18} /> : <Maximize size={18} />}
          </button>
        </div>
      </div>

      <Card className="flex-1 p-0 overflow-hidden relative border-primary/30" ref={containerRef}>
        {loading ? (
           <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/80 z-10 backdrop-blur-sm">
             <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
             <div className="mt-4 text-primary font-mono text-sm tracking-widest animate-pulse">MAPPING NETWORK ROUTES...</div>
           </div>
        ) : nodes.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-textMuted font-mono text-lg">NO NETWORK DATA AVAILABLE</p>
          </div>
        ) : (
          <ForceGraph3D
            ref={graphRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={graphData}
            nodeLabel={n => `<div style="background: rgba(10,10,15,0.9); padding: 8px; border: 1px solid ${n.color}; border-radius: 4px; font-family: monospace;">
                <b style="color: white">${n.name}</b><br/>
                Type: ${n.type}<br/>
                IP: ${n.ip}<br/>
                Status: <span style="color: ${n.color}">${n.status.toUpperCase()}</span>
              </div>`}
            nodeColor={n => n.color}
            nodeRelSize={1}
            nodeResolution={16}
            linkColor={l => l.color}
            linkWidth={l => l.bandwidth === '10 Gbps' ? 2 : l.bandwidth === '100 Gbps' ? 3 : 1}
            linkResolution={6}
            linkDirectionalParticles={l => l.status === 'active' ? 2 : 0}
            linkDirectionalParticleWidth={2}
            linkDirectionalParticleSpeed={0.01}
            backgroundColor="#0a0a0f"
            onNodeClick={n => {
              // Focus camera on clicked node
              const distance = 150;
              const distRatio = 1 + distance/Math.hypot(n.x, n.y, n.z);
              graphRef.current.cameraPosition(
                { x: n.x * distRatio, y: n.y * distRatio, z: n.z * distRatio }, 
                n, 
                1000  
              );
            }}
          />
        )}
        
        {/* Graph Overlay UI */}
        <div className="absolute bottom-4 left-4 bg-surfaceHighlight/80 backdrop-blur-md p-3 rounded border border-border flex flex-col space-y-2 pointer-events-none">
          <p className="text-xs font-mono text-textMuted mb-1 font-bold">NODE STATUS LEGEND</p>
          <div className="flex items-center text-xs font-mono text-textMain"><div className="w-3 h-3 rounded-full bg-[#00f0ff] mr-2 shadow-[0_0_5px_#00f0ff]"></div> ONLINE</div>
          <div className="flex items-center text-xs font-mono text-textMain"><div className="w-3 h-3 rounded-full bg-[#ffb300] mr-2 shadow-[0_0_5px_#ffb300]"></div> DEGRADED</div>
          <div className="flex items-center text-xs font-mono text-textMain"><div className="w-3 h-3 rounded-full bg-[#ff003c] mr-2 shadow-[0_0_5px_#ff003c]"></div> OFFLINE</div>
          
          <div className="mt-2 pt-2 border-t border-border flex justify-between text-[10px] font-mono text-textMuted">
            <span>NODES: {nodes.length}</span>
            <span>LINKS: {links.length}</span>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
