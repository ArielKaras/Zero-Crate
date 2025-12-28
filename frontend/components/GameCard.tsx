import React, { useEffect, useRef } from 'react';
import { GameOffer, OfferType, Source, VaultStatus } from '../types';

interface GameCardProps {
  offer: GameOffer;
  isFocused: boolean;
}

export const GameCard: React.FC<GameCardProps> = ({ offer, isFocused }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const isMystery = offer.type === OfferType.MYSTERY || offer.vaultStatus === VaultStatus.MYSTERY;

  // Scroll into view when focused
  useEffect(() => {
    if (isFocused && cardRef.current) {
      cardRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center',
      });
    }
  }, [isFocused]);

  // Platform Color Badges
  const getPlatformColor = () => {
    switch (offer.source) {
      case Source.STEAM: return 'bg-[#1b2838] text-blue-200';
      case Source.EPIC: return 'bg-[#333] text-white';
      case Source.GOG: return 'bg-[#5c2e7a] text-purple-200';
      default: return 'bg-zinc-800 text-zinc-300';
    }
  };

  return (
    <div
      ref={cardRef}
      className={`
        relative flex-shrink-0 rounded-sm transition-all duration-300 ease-out cursor-pointer overflow-visible
        ${isFocused 
          ? 'w-80 h-48 scale-110 z-20 shadow-[0_10px_40px_-10px_rgba(0,0,0,0.8)] ring-1 ring-white/20' 
          : 'w-72 h-40 opacity-80 hover:opacity-100 z-10 brightness-75'
        }
      `}
    >
      {/* 1. Cover Art Layer */}
      <div className="absolute inset-0 rounded-sm overflow-hidden bg-zinc-900">
        {!isMystery && offer.coverImage ? (
          <img 
            src={offer.coverImage} 
            alt={offer.title} 
            className="w-full h-full object-cover"
          />
        ) : (
          /* Fallback / Mystery Gradient */
          <div className="w-full h-full bg-gradient-to-br from-zinc-800 to-black relative">
             {isMystery && (
               <div className="absolute inset-0 flex items-center justify-center opacity-10 bg-[url('https://www.transparenttextures.com/patterns/diagmonds-light.png')]">
               </div>
             )}
          </div>
        )}
        
        {/* Cinematic Vignette Overlay */}
        <div className={`absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent transition-opacity duration-300 ${isFocused ? 'opacity-90' : 'opacity-60'}`}></div>
      </div>

      {/* 2. Content Layer */}
      <div className="absolute inset-0 p-4 flex flex-col justify-between">
        
        {/* Top: Badges (Only on Focus or if it's a critical window) */}
        <div className={`flex justify-between items-start transition-all duration-300 ${isFocused ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2'}`}>
          <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded shadow-sm ${getPlatformColor()}`}>
            {offer.source}
          </span>
          
          {offer.windowInfo && (
             <span className="text-[10px] font-bold text-white bg-red-600/80 px-1.5 py-0.5 rounded shadow-sm backdrop-blur-md">
               {offer.windowInfo}
             </span>
          )}
        </div>

        {/* Bottom: Title & Meta */}
        <div className={`transform transition-all duration-300 ${isFocused ? 'translate-y-0' : 'translate-y-1'}`}>
          
          {/* Mystery State */}
          {isMystery ? (
            <div className="text-center w-full mb-4">
               <span className="block text-3xl font-bold tracking-[0.5em] text-white/10 select-none animate-pulse">???</span>
               <span className={`text-xs uppercase tracking-widest text-theme-dim mt-2 block transition-opacity ${isFocused ? 'opacity-100' : 'opacity-0'}`}>
                 {offer.windowInfo || 'Unlocks Soon'}
               </span>
            </div>
          ) : (
            /* Normal State */
            <>
              <h3 className={`font-bold text-white leading-tight mb-1 shadow-black drop-shadow-md ${isFocused ? 'text-lg' : 'text-sm text-zinc-300'}`}>
                {offer.title}
              </h3>
              
              {/* Metadata Row (Focus Only) */}
              <div className={`flex items-center gap-2 text-xs overflow-hidden transition-all duration-300 ${isFocused ? 'h-6 opacity-100 mt-1' : 'h-0 opacity-0'}`}>
                 <span className="text-emerald-400 font-bold">FREE</span>
                 <span className="text-zinc-500 line-through decoration-zinc-500/50">${offer.marketValue.toFixed(2)}</span>
                 <span className="text-zinc-600 px-1">•</span>
                 <span className="text-zinc-400">{offer.expiresAt}</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* 3. Action Hints (Bottom right, Focus only) */}
      {isFocused && !isMystery && (
        <div className="absolute bottom-4 right-4 flex gap-2">
           <div className="w-6 h-6 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/20 shadow-lg">
             <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M14 5l7 7m0 0l-7 7m7-7H3" />
             </svg>
           </div>
        </div>
      )}
    </div>
  );
};