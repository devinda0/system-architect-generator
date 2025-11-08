import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import type { NodeProps } from "@xyflow/react";
import type { Component } from "../../types/architecture";

export interface ComponentNodeData {
  element: Component;
  label: string;
  technology?: string;
  width: number;
  height: number;
}

function ComponentNode({ data, selected }: NodeProps) {
  const nodeData = data as unknown as ComponentNodeData;

  return (
    <div
      className={`h-full px-4 py-3 rounded-lg border-2 bg-gradient-to-br from-purple-50 via-violet-50 to-indigo-50 backdrop-blur-sm transition-all duration-300 ${
        selected 
          ? "border-purple-500 shadow-xl shadow-purple-500/30 scale-[1.02]" 
          : "border-purple-300 shadow-md hover:shadow-lg hover:border-purple-400"
      }`}
      style={{ 
        width: `${nodeData.width}px`,
        minHeight: `${nodeData.height}px`
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-purple-600 !w-2.5 !h-2.5 !border-2 !border-white"
      />

      <div className="flex items-center gap-2 mb-3">
        <div className="w-2 h-2 rounded-sm bg-purple-600 animate-pulse" />
        <span className="text-xs font-bold text-purple-700 uppercase tracking-widest">
          Component
        </span>
      </div>

      <div className="font-bold text-gray-900 text-sm mb-2 leading-tight">
        {nodeData.label}
      </div>

      {nodeData.technology && (
        <div className="text-xs font-medium text-purple-700 bg-purple-100 px-2 py-1 rounded-md inline-block">
          {nodeData.technology}
        </div>
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-purple-600 !w-2.5 !h-2.5 !border-2 !border-white"
      />
    </div>
  );
}

export default memo(ComponentNode);
