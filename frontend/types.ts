export enum OfferType {
  GAME = 'Game',
  DLC = 'DLC',
  MYSTERY = 'Mystery',
}

export enum Source {
  EPIC = 'Epic',
  STEAM = 'Steam',
  GOG = 'GOG',
}

export enum Rating {
  VERY_POSITIVE = 'V.Positive',
  POSITIVE = 'Positive',
  MIXED = 'Mixed',
  UNKNOWN = 'Unknown',
}

export enum VaultStatus {
  LIVE = 'LIVE',
  UPCOMING = 'UPCOMING',
  MYSTERY = 'MYSTERY',
}

export interface GameOffer {
  id: string;
  source: Source;
  type: OfferType;
  title: string;
  coverImage: string; // The visual identity
  marketValue: number;
  rating: Rating;
  expiresAt: string; // Relative string or ISO
  isFreeNow: boolean;
  seen: boolean;
  url: string;
  vaultStatus?: VaultStatus;
  windowInfo?: string; // e.g., "ENDS IN 4h", "STARTS 04/18"
}

export interface PlayerState {
  level: number;
  title: string;
  xpBalance: number;
  streakStatus: 'ACTIVE' | 'INACTIVE';
  lastSignal: string;
  valueSecured: number;
  shieldLevel: 1 | 2 | 3;
}

export interface HistoryEntry {
  id: string;
  title: string;
  date: string;
  value: number;
}