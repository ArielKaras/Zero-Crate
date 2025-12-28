import React from 'react';
import { HistoryEntry } from '../types';

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  history: HistoryEntry[];
}

export const HistoryModal: React.FC<HistoryModalProps> = ({ isOpen, onClose, history }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-theme-bg border border-theme-border p-8 max-w-xl w-full shadow-2xl">
        <div className="flex justify-between items-baseline mb-6">
            <h2 className="text-theme-fg font-bold text-lg tracking-tight">Retail Value Log</h2>
            <span className="text-theme-dim text-xs">Total records: {history.length}</span>
        </div>
        
        <div className="space-y-1 text-sm text-theme-dim max-h-80 overflow-y-auto pr-2">
           <div className="grid grid-cols-12 pb-2 mb-2 font-medium text-theme-dim/50 text-xs border-b border-theme-border/50">
             <div className="col-span-3">DATE</div>
             <div className="col-span-7">TITLE</div>
             <div className="col-span-2 text-right">VALUE</div>
           </div>
           
           {history.length === 0 ? (
             <div className="text-center italic py-8 text-theme-dim/50">No records found</div>
           ) : (
             history.map((entry) => (
               <div key={entry.id} className="grid grid-cols-12 py-2 hover:bg-theme-surface rounded px-1 transition-colors">
                 <div className="col-span-3 text-xs opacity-70">{entry.date}</div>
                 <div className="col-span-7 truncate font-medium text-theme-fg">{entry.title}</div>
                 <div className="col-span-2 text-right text-theme-accent">${entry.value.toFixed(2)}</div>
               </div>
             ))
           )}
        </div>

        <div className="mt-6 text-center text-xs text-theme-dim/50">
          Press any key to close
        </div>
      </div>
    </div>
  );
};