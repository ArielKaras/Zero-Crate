import React from 'react';
import { GameOffer } from '../types';
import { GameCard } from './GameCard';

interface DiscoveryGridProps {
  title: string;
  offers: GameOffer[];
  selectedIndex: number;
  startIndex: number; // The global index offset
}

export const DiscoveryGrid: React.FC<DiscoveryGridProps> = ({ title, offers, selectedIndex, startIndex }) => {
  if (offers.length === 0) return null;

  return (
    <div className="mb-8">
      <h2 className="text-xs font-bold text-theme-dim uppercase tracking-widest mb-4 flex items-center gap-2">
        <div className="w-1 h-1 bg-theme-dim rounded-full"></div>
        {title}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {offers.map((offer, localIndex) => {
          const globalIndex = startIndex + localIndex;
          const isSelected = globalIndex === selectedIndex;
          
          return (
            <GameCard 
              key={offer.id} 
              offer={offer} 
              isFocused={isSelected} 
            />
          );
        })}
      </div>
    </div>
  );
};