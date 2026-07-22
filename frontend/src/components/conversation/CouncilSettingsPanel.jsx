import React, { useState, useEffect } from 'react';
import { Settings, X, Info } from 'lucide-react';

export function CouncilSettingsPanel({ weights, onWeightsChange, isOpen, onClose }) {
    // Local state for smooth dragging
    const [localWeights, setLocalWeights] = useState(weights);

    // Sync with external state if it changes
    useEffect(() => {
        setLocalWeights(weights);
    }, [weights]);

    const handleSliderChange = (agent, value) => {
        const newValue = parseInt(value, 10);
        
        let newWeights = { ...localWeights, [agent]: newValue };
        
        // Auto-normalize if total exceeds 100 (optional UX choice)
        // Here we just let them set whatever, but show the normalized percentages.
        
        setLocalWeights(newWeights);
    };

    const handleMouseUp = () => {
        // Only propagate changes when they release the slider to avoid too many re-renders
        onWeightsChange(localWeights);
    };

    const total = Object.values(localWeights).reduce((a, b) => a + b, 0);

    const getNormalized = (val) => {
        if (total === 0) return 0;
        return Math.round((val / total) * 100);
    };

    if (!isOpen) return null;

    return (
        <div className="w-80 border-l border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex flex-col h-full overflow-y-auto">
            <div className="flex items-center justify-between px-4 py-4 border-b border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2">
                    <Settings className="w-4 h-4 text-slate-500" />
                    <h3 className="font-semibold text-sm text-slate-900 dark:text-white">Council Settings</h3>
                </div>
                <button onClick={onClose} className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
                    <X className="w-4 h-4" />
                </button>
            </div>
            
            <div className="p-4 space-y-6">
                <div className="bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 p-3 rounded-lg text-xs flex gap-2">
                    <Info className="w-4 h-4 shrink-0" />
                    <p>Adjust the influence of each council member. The weights will automatically normalize to 100%.</p>
                </div>

                <div className="space-y-5">
                    {Object.entries(localWeights).map(([agent, val]) => (
                        <div key={agent} className="space-y-2">
                            <div className="flex justify-between items-center text-sm">
                                <span className="font-medium text-slate-700 dark:text-slate-300 capitalize">{agent}</span>
                                <span className="text-slate-500 dark:text-slate-400 font-mono text-xs">
                                    {getNormalized(val)}%
                                </span>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={val}
                                onChange={(e) => handleSliderChange(agent, e.target.value)}
                                onMouseUp={handleMouseUp}
                                onTouchEnd={handleMouseUp}
                                className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                            />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
