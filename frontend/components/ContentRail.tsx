import React from 'react';
import { GameOffer } from '../types';
import { GameCard } from './GameCard';

interface ContentRailProps {
  title: string;
  offers: GameOffer[];
  isActiveRow: boolean;
  focusedCardIndex: number;
}

export const ContentRail: React.FC<ContentRailProps> = ({ title, offers, isActiveRow, focusedCardIndex }) => {
  if (offers.length === 0) return null;

  return (
    <div className={`mb-8 transition-opacity duration-500 ${isActiveRow ? 'opacity-100' : 'opacity-40'}`}>
      <h2 className="px-12 text-xs font-bold text-theme-dim uppercase tracking-widest mb-3 flex items-center gap-2">
        <span className={`w-1.5 h-1.5 rounded-full transition-colors duration-300 ${isActiveRow ? 'bg-theme-accent shadow-[0_0_8px_#10b981]' : 'bg-transparent'}`}></span>
        {title}
      </h2>

      {/* Scroll Container */}
      <div className="flex gap-4 px-12 overflow-x-visible py-4 min-h-[220px]">
        {offers.map((offer, index) => (
          <GameCard 
            key={offer.id} 
            offer={offer} 
            isFocused={isActiveRow && index === focusedCardIndex}
          />
        ))}
        
        {/* Spacer for right padding */}
        <div className="w-12 flex-shrink-0"></div>
      </div>
    </div>
  );
};