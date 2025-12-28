import React from 'react';
import { GameOffer } from '../types';
import { GameCard } from './GameCard';

interface WatchlistProps {
  offers: GameOffer[];
  selectedIndex: number;
  startIndex: number;
}

export const Watchlist: React.FC<WatchlistProps> = ({ offers, selectedIndex, startIndex }) => {
  return (
    <div className="mb-8 pt-6 border-t border-theme-border/30">
      <h2 className="text-xs font-bold text-theme-dim uppercase tracking-widest mb-4 flex items-center gap-2">
        <div className="w-1 h-1 bg-theme-dim rounded-full"></div>
        Watchlist // Upcoming
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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