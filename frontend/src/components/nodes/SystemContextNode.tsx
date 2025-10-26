import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import type { NodeProps } from "@xyflow/react";
import type { SystemContext } from "../../types/architecture";

export interface SystemContextNodeData {
  element: SystemContext;
  label: string;
    width: number;
  height: number;
}

function SystemContextNode({ data, selected }: NodeProps) {
  const nodeData = data as unknown as SystemContextNodeData;

  return (
    <div
      className={`h-full w-[${nodeData.width}px] rounded-lg border-2 bg-blue-50 bg-opacity-30 ${
        selected ? "border-blue-600 shadow-lg" : "border-blue-400"
      }`}
      style={{ pointerEvents: 'all' }}
    >
      <Handle type="target" position={Position.Top} className="!bg-blue-600" />

      <div className="flex flex-col bg-blue-100 px-3 py-2 rounded-t-md border-b border-blue-300">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-600" />
          <span className="w-full text-xs font-semibold text-blue-800 uppercase tracking-wider">
            System Context
          </span>
        </div>
        <div className="flex-1" />
        <span className="font-bold text-blue-900 text-base">
          {nodeData.label}
        </span>
      </div>

      <div className="w-full flex-1 p-2" style={{ pointerEvents: 'none' }}></div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-blue-600"
      />
    </div>
  );
}

export default memo(SystemContextNode);
