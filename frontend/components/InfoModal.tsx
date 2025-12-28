import React from 'react';

interface InfoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const InfoModal: React.FC<InfoModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-theme-bg border border-theme-border p-8 max-w-md w-full shadow-2xl">
        <h2 className="text-theme-fg font-bold text-lg mb-6 tracking-tight">System Intelligence</h2>
        
        <div className="space-y-6 text-sm text-theme-dim">
          <div>
            <span className="text-theme-fg font-medium block mb-1">Source Signals</span>
            <p>Direct API intercepts from Steam, Epic, and GOG endpoints.</p>
          </div>
          <div>
            <span className="text-theme-fg font-medium block mb-1">Curation Logic</span>
            <p>Only tracking verified 100% discounts. Shovelware is filtered based on sensitivity settings.</p>
          </div>
          <div>
            <span className="text-theme-fg font-medium block mb-1">DLC Protocol</span>
            <p>Expansion content is only surfaced if the base game is verified Free-to-Play.</p>
          </div>
        </div>

        <div className="mt-8 text-center text-xs text-theme-dim/50">
          Press any key to close
        </div>
      </div>
    </div>
  );
};