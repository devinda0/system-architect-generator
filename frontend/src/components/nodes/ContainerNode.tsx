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
      className={`h-full w-[${
        nodeData.width
      }px] rounded-lg border-2 bg-orange-50 bg-opacity-40 ${
        selected ? "border-orange-600 shadow-lg" : "border-orange-400"
      }`}
      style={{ pointerEvents: 'all' }}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-orange-600"
      />

      <div
        className={`h-[${nodeData.height}px] w-[${nodeData.width}px] bg-orange-100 px-3 py-2 rounded-t-md border-b border-orange-300 mb-2`}
      >
        <div className="flex items-center gap-2 mb-1">
          <div className="w-2.5 h-2.5 rounded bg-orange-600" />
          <span className="text-xs font-semibold text-orange-800 uppercase tracking-wider">
            Container
          </span>
        </div>

        <div className="flex w-full ">
          <div className="font-bold text-gray-900">{nodeData.label}</div>

          {nodeData.technology && (
            <div className="ml-3 text-xs font-semibold px-2 py-1 text-white italic bg-orange-500 rounded-full ">
              {nodeData.technology}
            </div>
          )}
        </div>
      </div>

      <div className="w-full flex-1 p-2" style={{ pointerEvents: 'none' }}></div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-orange-600"
      />
    </div>
  );
}

export default memo(ContainerNode);
