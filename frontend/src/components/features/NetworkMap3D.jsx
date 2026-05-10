import React, { useEffect, useState, useRef, useMemo } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import { Card, CardHeader, CardTitle } from '../ui/Card';

export function NetworkMap3D({ devices, links }) {
  const fgRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const containerRef = useRef(null);

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight
        });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const graphData = useMemo(() => {
    // Transform API data to force-graph format
    // Nodes need 'id', links need 'source' and 'target' matching node 'id's
    const nodes = devices.map(d => ({
      id: d.id,
      name: d.device_name,
      status: d.status,
      type: d.device_type,
      val: 2 // size
    }));

    const validNodeIds = new Set(nodes.map(n => n.id));
    
    const formattedLinks = links
      .filter(l => validNodeIds.has(l.source_device_id) && validNodeIds.has(l.target_device_id))
      .map(l => ({
        source: l.source_device_id,
        target: l.target_device_id,
        color: l.status === 'active' ? '#00f0ff' : '#ff003c'
      }));

    return { nodes, links: formattedLinks };
  }, [devices, links]);

  // Handle node click to focus camera
  const handleNodeClick = (node) => {
    // Aim at node from outside it
    const distance = 40;
    const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);

    if (fgRef.current) {
      fgRef.current.cameraPosition(
        { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
        node, // lookAt ({ x, y, z })
        3000  // ms transition duration
      );
    }
  };

  const getNodeColor = (status) => {
    if (status === 'online') return '#00f0ff'; // Cyan
    if (status === 'offline') return '#ff003c'; // Red
    return '#ffb300'; // Yellow/Warning
  };

  return (
    <Card className="min-h-[400px] h-full flex flex-col relative overflow-hidden">
      <CardHeader className="absolute top-0 left-0 z-10 w-full p-6 bg-gradient-to-b from-surface/90 to-transparent">
        <CardTitle>IMMERSIVE NETWORK TOPOLOGY</CardTitle>
        <p className="text-xs text-textMuted tracking-wider mt-1">WebGL 3D NODE MAP</p>
      </CardHeader>
      
      <div ref={containerRef} className="flex-1 w-full h-full min-h-[400px]">
        {dimensions.width > 0 && graphData.nodes.length > 0 ? (
          <ForceGraph3D
            ref={fgRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={graphData}
            nodeId="id"
            nodeColor={node => getNodeColor(node.status)}
            nodeLabel="name"
            nodeResolution={16}
            linkColor="color"
            linkWidth={1}
            linkOpacity={0.3}
            linkResolution={6}
            onNodeClick={handleNodeClick}
            backgroundColor="#0a0a0f" // match background
            enableNodeDrag={false}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-textMuted">
            <span className="font-mono text-sm animate-pulse">INITIALIZING WEBGL SUBSYSTEM...</span>
          </div>
        )}
      </div>
      
      {/* Overlay decorations */}
      <div className="absolute bottom-4 right-4 pointer-events-none">
        <div className="text-right font-mono text-[10px] text-primary/50">
          X: {dimensions.width} Y: {dimensions.height}<br/>
          NODES: {graphData.nodes.length} LINKS: {graphData.links.length}
        </div>
      </div>
    </Card>
  );
}
