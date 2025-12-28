import React from 'react';

interface ControlsProps {
  dlcEnabled: boolean;
  shieldLevel: number;
}

export const Controls: React.FC<ControlsProps> = ({ dlcEnabled, shieldLevel }) => {
  return (
    <div className="fixed bottom-0 left-0 w-full bg-gradient-to-t from-theme-bg via-theme-bg to-transparent pb-6 pt-12 flex justify-center pointer-events-none z-50">
      <div className="flex gap-12 text-[10px] text-theme-dim uppercase tracking-widest font-medium">
        <span className="flex items-center gap-2">
          <span className="bg-white/10 px-1.5 py-0.5 rounded text-white">ARROWS</span> Navigate
        </span>
        <span className="flex items-center gap-2">
          <span className="bg-white/10 px-1.5 py-0.5 rounded text-white">ENTER</span> Open
        </span>
        <span className="flex items-center gap-2">
          <span className="bg-white/10 px-1.5 py-0.5 rounded text-white">I</span> Intelligence
        </span>
        <span className="flex items-center gap-2">
          <span className="bg-white/10 px-1.5 py-0.5 rounded text-white">H</span> Ledger
        </span>
      </div>
    </div>
  );
};
