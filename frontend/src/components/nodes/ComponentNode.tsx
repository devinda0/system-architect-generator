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
      className={`h-full w-[${nodeData.width}px] px-4 py-3 rounded-md border-2 bg-purple-50 ${
        selected ? "border-purple-600 shadow-lg" : "border-purple-400"
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-purple-600"
      />

      <div className="flex items-center gap-2 mb-1">
        <div className="w-2 h-2 rounded-sm bg-purple-600" />
        <span className="text-xs font-semibold text-purple-800 uppercase tracking-wider">
          Component
        </span>
      </div>

      <div className="w-full flex-1 p-2"></div>

      <div className="font-semibold text-gray-900 text-sm mb-1">
        {nodeData.label}
      </div>

      {nodeData.technology && (
        <div className="text-xs text-gray-600 italic">
          {nodeData.technology}
        </div>
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-purple-600"
      />
    </div>
  );
}

export default memo(ComponentNode);
