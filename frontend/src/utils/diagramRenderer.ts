import type { Node, Edge } from "@xyflow/react";
import type { SystemContext, Relationship } from "../types/architecture";

const componentWidth = 200;
const componentHeight = 100;
const systemContextWidth = 300;
const systemContextHeight = 240;

// Layout constants
const PADDING = 40;
const COMPONENT_SPACING_X = 30;
const COMPONENT_SPACING_Y = 20;
const CONTAINER_SPACING_X = 60;
const SYSTEM_PADDING = 50;

export function renderFromJSON(context: SystemContext): {
  nodes: Node[];
  edges: Edge[];
} {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  const allRelationships: Array<{
    sourceId: string;
    relationship: Relationship;
  }> = [];

  let systemContextTotalWidth = systemContextWidth;
  let systemContextTotalHeight = systemContextHeight;
  let containerX = SYSTEM_PADDING + PADDING;

  if (context.children && context.children.length > 0) {
    context.children.forEach((container) => {
      let componentX = PADDING;
      let componentY = 100; // Start below container header
      let maxComponentX = 0;
      let maxComponentY = 0;
      
      // Calculate components layout
      if (container.children && container.children.length > 0) {
        container.children.forEach((component, index) => {
          // Collect relationships
          if (component.relationships && component.relationships.length > 0) {
            component.relationships.forEach((rel) => {
              allRelationships.push({
                sourceId: component.id,
                relationship: rel,
              });
            });
          }

          // Create component node
          nodes.push({
            id: component.id,
            type: "component",
            position: { x: componentX, y: componentY },
            data: {
              element: component,
              label: component.name,
              technology: component.technology,
              width: componentWidth,
              height: componentHeight,
            },
            parentId: container.id,
            extent: "parent" as const,
          });

          maxComponentX = Math.max(maxComponentX, componentX + componentWidth);
          maxComponentY = Math.max(maxComponentY, componentY + componentHeight);

          // Position next component
          componentX += componentWidth + COMPONENT_SPACING_X;
          
          // Wrap to next row if needed (max 3 per row)
          if ((index + 1) % 3 === 0) {
            componentX = PADDING;
            componentY += componentHeight + COMPONENT_SPACING_Y;
          }
        });
      }

      // Calculate container dimensions
      const containerWidth = Math.max(
        280,
        maxComponentX + PADDING * 2
      );
      const containerHeight = Math.max(
        140,
        maxComponentY + PADDING
      );

      // Collect container relationships
      if (container.relationships && container.relationships.length > 0) {
        container.relationships.forEach((rel) => {
          allRelationships.push({ sourceId: container.id, relationship: rel });
        });
      }

      // Create container node
      nodes.unshift({
        id: container.id,
        type: "container",
        position: { x: containerX, y: SYSTEM_PADDING + PADDING },
        data: {
          element: container,
          label: container.name,
          technology: container.technology,
          width: containerWidth,
          height: containerHeight,
        },
        width: containerWidth,
        height: containerHeight,
        parentId: context.id,
        extent: "parent" as const,
      });

      // Update system context dimensions
      systemContextTotalWidth = Math.max(
        systemContextTotalWidth,
        containerX + containerWidth + SYSTEM_PADDING + PADDING
      );
      systemContextTotalHeight = Math.max(
        systemContextTotalHeight,
        containerHeight + SYSTEM_PADDING + PADDING * 2
      );

      // Position next container
      containerX += containerWidth + CONTAINER_SPACING_X;
    });
  }

  // Collect system context relationships
  if (context.relationships && context.relationships.length > 0) {
    context.relationships.forEach((rel) => {
      allRelationships.push({ sourceId: context.id, relationship: rel });
    });
  }

  // Create system context node
  nodes.unshift({
    id: context.id,
    type: "systemContext",
    position: { x: 50, y: 50 },
    data: {
      element: context,
      label: context.name,
      width: systemContextTotalWidth,
      height: systemContextTotalHeight,
    },
    width: systemContextTotalWidth,
    height: systemContextTotalHeight,
  });


  // Create edges from all relationships with premium styling
  allRelationships.forEach(({ sourceId, relationship }) => {
    edges.push({
      id: `${sourceId}-${relationship.targetId}`,
      source: sourceId,
      target: relationship.targetId,
      label: relationship.description,
      type: "smoothstep",
      animated: true,
      style: { 
        stroke: "#6366f1", 
        strokeWidth: 2.5,
        strokeDasharray: "0"
      },
      labelStyle: { 
        fill: "#1e293b", 
        fontSize: 12,
        fontWeight: 500
      },
      labelBgStyle: { 
        fill: "#ffffff", 
        fillOpacity: 0.95
      },
    });
  });

  console.log("Rendered Nodes:", nodes);
  console.log("Rendered Edges:", edges);
  return { nodes, edges };
}
