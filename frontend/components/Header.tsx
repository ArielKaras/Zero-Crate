import React from 'react';

export const Header: React.FC = () => {
  return (
    <div className="px-12 pt-8 pb-4 flex justify-between items-center opacity-80">
      <div className="text-base font-bold tracking-tight text-white/50">
        ZeroCrate
      </div>
      <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-theme-dim">
        <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
        Scout Online
        <span className="text-theme-border mx-1">|</span>
        Last Discovery 14h ago
      </div>
    </div>
  );
};
