import { useAppStore } from '../store/appStore';
import type { NodeData } from '../types/architecture';

export default function NodeDrawer() {
  const { selectedNode, setSelectedNode, isDrawerOpen } = useAppStore();

  if (!isDrawerOpen || !selectedNode) return null;

  const nodeData = selectedNode.data as unknown as NodeData;

  return (
    <>
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-20 z-10"
        onClick={() => setSelectedNode(null)}
      />

      {/* Drawer */}
      <div className="absolute left-0 top-0 bottom-0 w-80 bg-white shadow-xl z-20 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-4 py-3 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-800">Node Details</h2>
          <button
            onClick={() => setSelectedNode(null)}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <p className="text-gray-900">{nodeData?.label || selectedNode.id}</p>
          </div>

          {/* Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <p className="text-gray-900">{nodeData?.element?.type || 'Unknown'}</p>
          </div>

          {/* Description */}
          {nodeData?.description && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <p className="text-gray-900">{nodeData.description}</p>
            </div>
          )}

          {/* Technology */}
          {nodeData?.technology && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Technology
              </label>
              <p className="text-gray-900">{nodeData.technology}</p>
            </div>
          )}

          {/* Actions */}
          <div className="pt-4 border-t border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Actions
            </label>
            <div className="space-y-2">
              <button className="w-full px-4 py-2 text-sm text-left bg-blue-50 text-blue-700 rounded hover:bg-blue-100">
                Suggest Technology
              </button>
              <button className="w-full px-4 py-2 text-sm text-left bg-green-50 text-green-700 rounded hover:bg-green-100">
                Decompose into Components
              </button>
              <button className="w-full px-4 py-2 text-sm text-left bg-purple-50 text-purple-700 rounded hover:bg-purple-100">
                Suggest API Endpoints
              </button>
              <button className="w-full px-4 py-2 text-sm text-left bg-amber-50 text-amber-700 rounded hover:bg-amber-100">
                Refactor Element
              </button>
            </div>
          </div>

          {/* Relationships */}
          {nodeData?.element?.relationships && nodeData.element.relationships.length > 0 && (
            <div className="pt-4 border-t border-gray-200">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Relationships
              </label>
              <ul className="space-y-2">
                {nodeData.element.relationships.map((rel, index) => (
                  <li key={index} className="text-sm text-gray-600">
                    → {rel.description} ({rel.targetId})
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
