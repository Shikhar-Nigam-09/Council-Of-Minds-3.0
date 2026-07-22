import React, { useState, useEffect } from 'react';
import { AgentSlider } from './AgentSlider';
import { PlannerSourceBadge } from './PlannerSourceBadge';
import { Button } from '../ui/Button';

export const CouncilWeightPanel = ({ configuration, onConfirm, isConfirming }) => {
    const [weights, setWeights] = useState({
        logical: 20, practical: 20, analytical: 20, skeptical: 20, ethics: 20
    });
    const [enabled, setEnabled] = useState({
        logical: true, practical: true, analytical: true, skeptical: true, ethics: true
    });

    useEffect(() => {
        if (configuration) {
            setWeights({
                logical: configuration.logical_weight,
                practical: configuration.practical_weight,
                analytical: configuration.analytical_weight,
                skeptical: configuration.skeptical_weight,
                ethics: configuration.ethics_weight
            });
            setEnabled({
                logical: configuration.logical_enabled ?? true,
                practical: configuration.practical_enabled ?? true,
                analytical: configuration.analytical_enabled ?? true,
                skeptical: configuration.skeptical_enabled ?? true,
                ethics: configuration.ethics_enabled ?? true,
            });
        }
    }, [configuration]);

    const agents = ['logical', 'practical', 'analytical', 'skeptical', 'ethics'];

    const handleConfirm = () => {
        onConfirm({ weights, enabled });
    };

    const isAnyEnabled = Object.values(enabled).some(Boolean);

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-4 border dark:border-gray-700">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Council Configuration</h3>
                <PlannerSourceBadge source={configuration?.source} />
            </div>
            
            <div className="space-y-2 mb-8">
                {agents.map(agent => (
                    <AgentSlider
                        key={agent}
                        agent={agent}
                        weight={weights[agent]}
                        enabled={enabled[agent]}
                        onWeightChange={(val) => setWeights(prev => ({ ...prev, [agent]: val }))}
                        onEnabledChange={(val) => setEnabled(prev => ({ ...prev, [agent]: val }))}
                    />
                ))}
            </div>
            
            {!isAnyEnabled && (
                <div className="text-red-500 text-sm mb-4">
                    At least one agent must be enabled.
                </div>
            )}
            
            <div className="flex justify-end">
                <Button 
                    onClick={handleConfirm} 
                    disabled={!isAnyEnabled || isConfirming}
                >
                    {isConfirming ? 'Confirming...' : 'Continue'}
                </Button>
            </div>
        </div>
    );
};
