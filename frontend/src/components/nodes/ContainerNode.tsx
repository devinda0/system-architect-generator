import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import type { NodeProps } from "@xyflow/react";
import type { Container } from "../../types/architecture";

export interface ContainerNodeData {
  element: Container;
  label: string;
  technology?: string;
  width: number;
  height: number;
}

function ContainerNode({ data, selected }: NodeProps) {
  const nodeData = data as unknown as ContainerNodeData;

  return (
    <div
      className={`h-full rounded-xl border-3 bg-gradient-to-br from-orange-50 via-amber-50/80 to-yellow-50 backdrop-blur-sm transition-all duration-300 ${
        selected 
          ? "border-orange-500 shadow-2xl shadow-orange-500/30 scale-[1.02]" 
          : "border-orange-300 shadow-lg hover:shadow-xl hover:border-orange-400"
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
        className="!bg-orange-600 !w-3 !h-3 !border-2 !border-white"
      />

      <div className="bg-gradient-to-r from-orange-500 to-amber-500 px-4 py-3 rounded-t-lg border-b-2 border-orange-300 shadow-md">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 rounded-sm bg-white animate-pulse" />
          <span className="text-xs font-bold text-orange-100 uppercase tracking-widest">
            Container
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="font-bold text-white text-base drop-shadow-md">
            {nodeData.label}
          </div>

          {nodeData.technology && (
            <div className="text-xs font-semibold px-3 py-1 text-orange-900 bg-white/90 rounded-full backdrop-blur-sm shadow-sm">
              {nodeData.technology}
            </div>
          )}
        </div>
      </div>

      <div className="w-full flex-1 p-2" style={{ pointerEvents: 'none' }}></div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-orange-600 !w-3 !h-3 !border-2 !border-white"
      />
    </div>
  );
}

export default memo(ContainerNode);
