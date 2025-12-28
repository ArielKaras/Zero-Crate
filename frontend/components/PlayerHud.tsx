import React from 'react';
import { PlayerState } from '../types';

interface PlayerHudProps {
  state: PlayerState;
}

export const PlayerHud: React.FC<PlayerHudProps> = ({ state }) => {
  const { valueSecured, level, title } = state;

  return (
    <div className="px-12 mb-10 pt-4">
      <div className="flex flex-col items-start opacity-90">
        <span className="text-[10px] font-bold text-theme-dim uppercase tracking-widest mb-2 flex items-center gap-2">
           <span className="w-2 h-px bg-theme-dim"></span>
           Total Value Secured
        </span>
        <div className="flex items-baseline gap-6">
          <h1 className="text-7xl font-bold text-white tracking-tighter drop-shadow-2xl">
            ${valueSecured.toFixed(2)}
          </h1>
          
          <div className="flex items-center gap-3 text-xs font-medium text-theme-dim border-l border-theme-border/50 pl-6 h-10 opacity-60">
            <span className="uppercase tracking-wider">Lvl {level} {title}</span>
            <span className="text-theme-accent">• Streak Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};