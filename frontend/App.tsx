import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Header } from './components/Header';
import { PlayerHud } from './components/PlayerHud';
import { ContentRail } from './components/ContentRail';
import { Controls } from './components/Controls';
import { InfoModal } from './components/InfoModal';
import { HistoryModal } from './components/HistoryModal';
import { INITIAL_OFFERS, VAULT_OFFERS } from './constants';
import { PlayerState, GameOffer, OfferType, HistoryEntry } from './types';

const INITIAL_PLAYER_STATE: PlayerState = {
  level: 5,
  title: 'SCAVENGER',
  xpBalance: 14250,
  streakStatus: 'ACTIVE',
  lastSignal: '14h ago',
  valueSecured: 428.32,
  shieldLevel: 2,
};

// Define Categories
interface RailData {
  id: string;
  title: string;
  items: GameOffer[];
}

function App() {
  const [playerState, setPlayerState] = useState<PlayerState>(INITIAL_PLAYER_STATE);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  
  // Navigation State
  const [activeRowIndex, setActiveRowIndex] = useState(0);
  const [activeCardIndex, setActiveCardIndex] = useState(0);

  // Modals
  const [showInfo, setShowInfo] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  // Categorize Content
  const rails: RailData[] = useMemo(() => {
    // 1. Free Right Now
    const freeNow = INITIAL_OFFERS.filter(o => o.isFreeNow).sort((a,b) => b.marketValue - a.marketValue);
    
    // 2. High Value (> $20)
    const highValue = INITIAL_OFFERS.filter(o => o.marketValue >= 20);

    // 3. Ending Soon (Mock filter: contains 'h' for hours or < 2 days)
    const endingSoon = INITIAL_OFFERS.filter(o => o.expiresAt.includes('h'));

    // 4. Watchlist (Vault)
    const watchlist = VAULT_OFFERS;

    return [
      { id: 'free', title: 'Free Right Now', items: freeNow },
      { id: 'high_value', title: 'High Value Finds', items: highValue },
      { id: 'ending', title: 'Ending Soon', items: endingSoon },
      { id: 'watchlist', title: 'Watchlist // Upcoming', items: watchlist },
    ].filter(r => r.items.length > 0);
  }, []);

  // Keyboard Navigation
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (showInfo || showHistory) {
      if (e.key === 'Escape') {
        setShowInfo(false);
        setShowHistory(false);
      }
      return;
    }

    const currentRail = rails[activeRowIndex];
    const maxRow = rails.length - 1;
    const maxCol = currentRail ? currentRail.items.length - 1 : 0;

    switch (e.key) {
      case 'ArrowUp':
        e.preventDefault();
        if (activeRowIndex > 0) {
          setActiveRowIndex(prev => prev - 1);
          // Clamp column index for the new row
          const prevRowLength = rails[activeRowIndex - 1].items.length;
          setActiveCardIndex(prev => Math.min(prev, prevRowLength - 1));
        }
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (activeRowIndex < maxRow) {
          setActiveRowIndex(prev => prev + 1);
          // Clamp column index for the new row
          const nextRowLength = rails[activeRowIndex + 1].items.length;
          setActiveCardIndex(prev => Math.min(prev, nextRowLength - 1));
        }
        break;
      case 'ArrowLeft':
        e.preventDefault();
        setActiveCardIndex(prev => Math.max(0, prev - 1));
        break;
      case 'ArrowRight':
        e.preventDefault();
        setActiveCardIndex(prev => Math.min(maxCol, prev + 1));
        break;
      
      case 'Enter':
        const offer = currentRail.items[activeCardIndex];
        if (offer && offer.url) {
           window.open(offer.url, '_blank');
           
           // Mock: Add value on "open"
           setPlayerState(prev => ({
             ...prev,
             valueSecured: prev.valueSecured + offer.marketValue
           }));
           setHistory(prev => [{
               id: Date.now().toString(),
               title: offer.title,
               date: new Date().toISOString().split('T')[0],
               value: offer.marketValue
             }, ...prev]);
        }
        break;

      case 'i':
      case 'I':
        setShowInfo(true);
        break;
      case 'h':
      case 'H':
        setShowHistory(true);
        break;
    }
  }, [activeRowIndex, activeCardIndex, rails, showInfo, showHistory]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className="min-h-screen bg-theme-bg text-theme-fg font-mono overflow-hidden">
      <div className="flex flex-col h-screen">
        <Header />
        
        {/* Scrollable Main Content */}
        <div className="flex-grow overflow-y-auto overflow-x-hidden no-scrollbar">
          <PlayerHud state={playerState} />

          <div className="pb-24">
            {rails.map((rail, index) => (
              <ContentRail 
                key={rail.id}
                title={rail.title}
                offers={rail.items}
                isActiveRow={index === activeRowIndex}
                focusedCardIndex={index === activeRowIndex ? activeCardIndex : -1}
              />
            ))}
          </div>
        </div>

        <Controls dlcEnabled={false} shieldLevel={playerState.shieldLevel} />
      </div>
      
      <InfoModal isOpen={showInfo} onClose={() => setShowInfo(false)} />
      <HistoryModal isOpen={showHistory} onClose={() => setShowHistory(false)} history={history} />
    </div>
  );
}

export default App;
