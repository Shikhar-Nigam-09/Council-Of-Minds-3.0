import React from 'react';

export const AgentSlider = ({ agent, weight, enabled, onWeightChange, onEnabledChange }) => {
    return (
        <div className="flex items-center gap-4 py-2">
            <div className="w-24 font-medium capitalize text-sm">{agent}</div>
            <label className="relative inline-flex items-center cursor-pointer">
                <input 
                    type="checkbox" 
                    className="sr-only peer" 
                    checked={enabled}
                    onChange={(e) => onEnabledChange(e.target.checked)}
                />
                <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
            <input 
                type="range" 
                min="0" 
                max="100" 
                value={weight} 
                onChange={(e) => onWeightChange(parseInt(e.target.value, 10))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 disabled:opacity-50"
                disabled={!enabled}
            />
            <div className="w-12 text-right text-sm text-gray-500">{enabled ? weight : 0}%</div>
        </div>
    );
};
