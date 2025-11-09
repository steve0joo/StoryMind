import { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

/**
 * CharacterGraph - Interactive 2D force-directed graph for character relationships
 *
 * Shows characters as nodes and their relationships as links
 * Uses react-force-graph-2d for visualization
 */
function CharacterGraph({ characters, onNodeClick }) {
  const graphRef = useRef();
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    // Update dimensions based on container
    const updateDimensions = () => {
      const container = graphRef.current?.parentElement;
      if (container) {
        setDimensions({
          width: container.clientWidth || 800,
          height: Math.min(container.clientHeight || 600, 600)
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (!characters || characters.length === 0) {
      setGraphData({ nodes: [], links: [] });
      return;
    }

    // Transform characters into graph nodes
    const nodes = characters.map((char, index) => ({
      id: char.id,
      name: char.name,
      description: char.canonical_description?.substring(0, 100) + '...' || 'No description',
      mentionCount: char.mention_count || 0,
      // Size based on mention count (more mentions = bigger node)
      val: Math.max(5, Math.min(20, (char.mention_count || 1) / 2)),
      // Color based on mention count (gradient from light to dark blue)
      color: getNodeColor(char.mention_count || 0),
      x: Math.cos((index / characters.length) * 2 * Math.PI) * 100,
      y: Math.sin((index / characters.length) * 2 * Math.PI) * 100,
    }));

    // Extract relationships from characters
    // Assuming relationships are stored as JSON string in character.relationships
    const links = [];
    characters.forEach(char => {
      if (char.relationships) {
        try {
          const relationships = typeof char.relationships === 'string'
            ? JSON.parse(char.relationships)
            : char.relationships;

          if (Array.isArray(relationships)) {
            relationships.forEach(rel => {
              // Find target character by name
              const targetChar = characters.find(c =>
                c.name.toLowerCase() === rel.character?.toLowerCase()
              );

              if (targetChar) {
                links.push({
                  source: char.id,
                  target: targetChar.id,
                  relationship: rel.relationship || 'related',
                  value: 1
                });
              }
            });
          }
        } catch (e) {
          console.warn('Failed to parse relationships for', char.name, e);
        }
      }
    });

    // If no explicit relationships, create connections based on mention counts
    // (Characters with high mentions are likely to be related)
    if (links.length === 0 && nodes.length > 1) {
      // Connect each character to the most mentioned character
      const sortedByMentions = [...nodes].sort((a, b) => b.mentionCount - a.mentionCount);
      const mainCharacter = sortedByMentions[0];

      nodes.forEach(node => {
        if (node.id !== mainCharacter.id) {
          links.push({
            source: node.id,
            target: mainCharacter.id,
            relationship: 'appears with',
            value: 1
          });
        }
      });

      // Add some cross-connections between secondary characters
      for (let i = 1; i < Math.min(sortedByMentions.length, 4); i++) {
        for (let j = i + 1; j < Math.min(sortedByMentions.length, 4); j++) {
          if (Math.random() > 0.5) { // 50% chance of connection
            links.push({
              source: sortedByMentions[i].id,
              target: sortedByMentions[j].id,
              relationship: 'interacts with',
              value: 0.5
            });
          }
        }
      }
    }

    setGraphData({ nodes, links });
  }, [characters]);

  const getNodeColor = (mentionCount) => {
    // Gradient from light blue (few mentions) to dark blue (many mentions)
    const intensity = Math.min(255, 100 + mentionCount * 5);
    return `rgb(${255 - intensity}, ${255 - intensity}, 255)`;
  };

  const handleNodeClick = (node) => {
    if (onNodeClick) {
      const character = characters.find(c => c.id === node.id);
      onNodeClick(character);
    }
  };

  if (!characters || characters.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <p className="text-gray-500">No characters to display</p>
      </div>
    );
  }

  return (
    <div className="relative w-full" style={{ height: dimensions.height }}>
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        width={dimensions.width}
        height={dimensions.height}
        nodeLabel={node => `
          <div class="bg-white p-2 rounded shadow-lg border border-gray-200">
            <div class="font-bold text-sm">${node.name}</div>
            <div class="text-xs text-gray-600">Mentions: ${node.mentionCount}</div>
            <div class="text-xs text-gray-500 mt-1 max-w-xs">${node.description}</div>
          </div>
        `}
        nodeColor={node => node.color}
        nodeVal={node => node.val}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12/globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = '#333';
          ctx.fillText(label, node.x, node.y + node.val + 10/globalScale);
        }}
        nodeCanvasObjectMode={() => 'after'}
        linkLabel={link => link.relationship || 'related'}
        linkColor={() => 'rgba(100, 100, 100, 0.2)'}
        linkWidth={link => link.value || 1}
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={2}
        linkDirectionalParticleSpeed={0.005}
        onNodeClick={handleNodeClick}
        onNodeHover={node => {
          document.body.style.cursor = node ? 'pointer' : 'default';
        }}
        cooldownTicks={100}
        enableZoomPanInteraction={true}
        enableNodeDrag={true}
        d3VelocityDecay={0.3}
      />

      {/* Legend */}
      <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-md border border-gray-200">
        <h4 className="text-sm font-semibold mb-2">Legend</h4>
        <div className="text-xs space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-200"></div>
            <span>Few mentions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-600"></div>
            <span>Many mentions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-gray-300"></div>
            <span>Relationship</span>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2">Click & drag nodes</p>
      </div>

      {/* Instructions */}
      <div className="absolute bottom-4 left-4 bg-white p-2 rounded shadow-sm border border-gray-200">
        <p className="text-xs text-gray-600">
          💡 <span className="font-medium">Tip:</span> Scroll to zoom, drag to pan, click nodes for details
        </p>
      </div>
    </div>
  );
}

export default CharacterGraph;
