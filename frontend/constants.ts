import { GameOffer, OfferType, Rating, Source, VaultStatus } from './types';

// Using Steam header images for reliable 16:9-ish aspect ratio fallback
// In production, a resolver would fetch these from store APIs

export const INITIAL_OFFERS: GameOffer[] = [
  {
    id: '1',
    source: Source.EPIC,
    type: OfferType.GAME,
    title: 'The Outer Worlds: Spacer\'s Choice',
    coverImage: 'https://cdn.cloudflare.steamstatic.com/steam/apps/578650/header.jpg',
    marketValue: 59.99,
    rating: Rating.VERY_POSITIVE,
    expiresAt: '2d 14h',
    isFreeNow: true,
    seen: false,
    url: 'https://store.epicgames.com',
  },
  {
    id: '2',
    source: Source.STEAM,
    type: OfferType.DLC,
    title: 'Destiny 2: Legacy Collection',
    coverImage: 'https://cdn.cloudflare.steamstatic.com/steam/apps/1085660/header.jpg',
    marketValue: 19.99,
    rating: Rating.POSITIVE,
    expiresAt: '18h 04m',
    isFreeNow: true,
    seen: false,
    url: 'https://store.steampowered.com',
  },
  {
    id: '3',
    source: Source.EPIC,
    type: OfferType.GAME,
    title: 'Thief',
    coverImage: 'https://cdn.cloudflare.steamstatic.com/steam/apps/239160/header.jpg',
    marketValue: 19.99,
    rating: Rating.POSITIVE,
    expiresAt: '6d 22h',
    isFreeNow: true,
    seen: false,
    url: 'https://store.epicgames.com',
  },
  {
    id: '4',
    source: Source.GOG,
    type: OfferType.GAME,
    title: 'Deus Ex: Mankind Divided',
    coverImage: 'https://cdn.cloudflare.steamstatic.com/steam/apps/337000/header.jpg',
    marketValue: 29.99,
    rating: Rating.VERY_POSITIVE,
    expiresAt: '1d 02h',
    isFreeNow: true,
    seen: false,
    url: 'https://www.gog.com',
  },
  {
    id: '5',
    source: Source.STEAM,
    type: OfferType.GAME,
    title: '100% Orange Juice',
    coverImage: 'https://cdn.cloudflare.steamstatic.com/steam/apps/282800/header.jpg',
    marketValue: 6.99,
    rating: Rating.MIXED,
    expiresAt: '5h 30m',
    isFreeNow: true,
    seen: false,
    url: 'https://store.steampowered.com',
  }
];

export const VAULT_OFFERS: GameOffer[] = [
  {
    id: 'v1',
    source: Source.STEAM,
    type: OfferType.GAME,
    title: 'Content Warning',
    coverImage: 'https://cdn.cloudflare.steamstatic.com/steam/apps/2881650/header.jpg',
    marketValue: 0.00,
    rating: Rating.VERY_POSITIVE,
    expiresAt: '',
    isFreeNow: false,
    seen: true,
    url: '',
    vaultStatus: VaultStatus.LIVE,
    windowInfo: 'ENDS IN 4h'
  },
  {
    id: 'v2',
    source: Source.EPIC,
    type: OfferType.GAME,
    title: 'Ghostrunner',
    coverImage: 'https://cdn.cloudflare.steamstatic.com/steam/apps/1139900/header.jpg',
    marketValue: 29.99,
    rating: Rating.POSITIVE,
    expiresAt: '',
    isFreeNow: false,
    seen: false,
    url: '',
    vaultStatus: VaultStatus.UPCOMING,
    windowInfo: 'STARTS 04/11'
  },
  {
    id: 'v3',
    source: Source.EPIC,
    type: OfferType.MYSTERY,
    title: '[ REDACTED ]',
    coverImage: '', // Mystery cards use a generated pattern
    marketValue: 0,
    rating: Rating.UNKNOWN,
    expiresAt: '',
    isFreeNow: false,
    seen: false,
    url: '',
    vaultStatus: VaultStatus.MYSTERY,
    windowInfo: 'STARTS 04/18'
  }
];