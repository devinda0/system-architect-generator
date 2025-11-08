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
      className={`h-full rounded-xl border-4 bg-gradient-to-br from-blue-50 via-blue-100/50 to-indigo-50 backdrop-blur-sm transition-all duration-300 ${
        selected 
          ? "border-blue-500 shadow-2xl shadow-blue-500/30 scale-[1.02]" 
          : "border-blue-300 shadow-xl hover:shadow-2xl hover:border-blue-400"
      }`}
      style={{ 
        pointerEvents: 'all',
        width: `${nodeData.width}px`,
        minHeight: `${nodeData.height}px`
      }}
    >
      <Handle 
        type="target" 
        position={Position.Top} 
        className="!bg-blue-600 !w-3 !h-3 !border-2 !border-white" 
      />

      <div className="flex flex-col bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 rounded-t-lg border-b-2 border-blue-400 shadow-md">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-2.5 h-2.5 rounded-full bg-white animate-pulse" />
          <span className="text-xs font-bold text-blue-100 uppercase tracking-widest">
            System Context
          </span>
        </div>
        <span className="font-bold text-white text-lg drop-shadow-md">
          {nodeData.label}
        </span>
      </div>

      <div className="w-full flex-1 p-2" style={{ pointerEvents: 'none' }}></div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-blue-600 !w-3 !h-3 !border-2 !border-white"
      />
    </div>
  );
}

export default memo(SystemContextNode);
