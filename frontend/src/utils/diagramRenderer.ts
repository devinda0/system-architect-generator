import type { Node, Edge } from "@xyflow/react";
import type { SystemContext, Relationship } from "../types/architecture";

interface LayoutNode {
  id: string;
  width: number;
  height: number;
  x?: number;
  y?: number;
}

const componentWidth = 180;
const componentHeight = 90;
const containerWidth = 220;
const containerHeight = 120;
const systemContextWidth = 240;
const systemContextHeight = 200;

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

  const levelNodes = new Map<number, LayoutNode[]>();

  const containerNodes: LayoutNode[] = [];
  let minContainerFitWidth = 0;
  let minContainerFitHeight = 0;
  let posX = 100;
  if (context.children && context.children.length > 0) {
    context.children.forEach((container) => {
      const componentNodes: LayoutNode[] = [];
      let minFitWidth = 0;
      let minFitHeight = 0;
      let coordX = 50;
      if (container.children && container.children.length > 0) {
        container.children.forEach((component, index) => {
          componentNodes.push({
            id: component.id,
            width: componentWidth,
            height: componentHeight,
          });
          minFitWidth += componentWidth + 50;
          minFitHeight += componentHeight;
          component.relationships.forEach((rel) => {
            allRelationships.push({
              sourceId: component.id,
              relationship: rel,
            });
          });

          

          nodes.push({
            id: component.id,
            type: "component",
            position: { x: coordX, y: 80 },
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

          coordX += componentWidth + 50;
        });

        levelNodes.set(2, [...(levelNodes.get(2) || []), ...componentNodes]);
      }

      const width = Math.max(containerWidth, minFitWidth);
      const height = Math.max(containerHeight, minFitHeight);
      containerNodes.push({
        id: container.id,
        width: width,
        height: height,
      });
      minContainerFitWidth += width + 150;
      minContainerFitHeight += height;

      container.relationships.forEach((rel) => {
        allRelationships.push({ sourceId: container.id, relationship: rel });
      });

      nodes.unshift({
        id: container.id,
        type: "container",
        position: { x: posX, y: 120 },
        data: {
          element: container,
          label: container.name,
          technology: container.technology,
          width: width,
          height: height,
        },
        width: width,
        height: height,
        parentId: context.id,
        extent: "parent" as const,
      });
      posX += width + 100;
    });

    levelNodes.set(1, containerNodes);
  }

  levelNodes.set(0, [
    {
      id: context.id,
      width: Math.max(systemContextWidth, minContainerFitWidth),
      height: Math.max(systemContextHeight, minContainerFitHeight),
    },
  ]);

  // Collect relationships from SystemContext
  context.relationships.forEach((rel) => {
    allRelationships.push({ sourceId: context.id, relationship: rel });
  });

  nodes.unshift({
    id: context.id,
    type: "systemContext",
    position: { x: 0, y: 0 }, // Will be updated after layout
    data: {
      element: context,
      label: context.name,
      width: Math.max(systemContextWidth, minContainerFitWidth),
      height: Math.max(systemContextHeight, minContainerFitHeight),
    },
    width: Math.max(systemContextWidth, minContainerFitWidth),
    height: Math.max(systemContextHeight, minContainerFitHeight),
  });


  // Create edges from all relationships
  allRelationships.forEach(({ sourceId, relationship }) => {
    edges.push({
      id: `${sourceId}-${relationship.targetId}`,
      source: sourceId,
      target: relationship.targetId,
      label: relationship.description,
      type: "smoothstep",
      animated: false,
      style: { stroke: "#64748b", strokeWidth: 2 },
      labelStyle: { fill: "#475569", fontSize: 12 },
      labelBgStyle: { fill: "#f8fafc", fillOpacity: 0.9 },
    });
  });

  console.log("Rendered Nodes:", nodes);
  console.log("Rendered Edges:", edges);
  return { nodes, edges };
}
