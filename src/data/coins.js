export const coins = [
  {
    id: "bitcoin",
    name: "Bitcoin",
    symbol: "BTC",
    price: 67245.32,
    change1h: 0.25,
    change24h: 2.15,
    change7d: 5.32,
    volume: 38521456789,
    marketCap: 1323456789012,
    categories: ["store-of-value", "pow", "layer-1"],
  },
  {
    id: "ethereum",
    name: "Ethereum",
    symbol: "ETH",
    price: 3245.67,
    change1h: 0.15,
    change24h: 1.85,
    change7d: 4.21,
    volume: 15234567890,
    marketCap: 389012345678,
    categories: ["smart-contracts", "defi", "nft", "layer-1"],
  },
  {
    id: "singularitynet",
    name: "SingularityNET",
    symbol: "AGIX",
    price: 0.98,
    change1h: 2.5,
    change24h: 15.2,
    change7d: 45.8,
    volume: 234567890,
    marketCap: 1234567890,
    categories: ["ai", "blockchain-ai", "ethereum"],
  },
  {
    id: "fetch-ai",
    name: "Fetch.ai",
    symbol: "FET",
    price: 2.15,
    change1h: 1.8,
    change24h: 12.5,
    change7d: 38.2,
    volume: 189567890,
    marketCap: 987654321,
    categories: ["ai", "blockchain-ai", "smart-contracts", "cosmos"],
  },
  {
    id: "ocean-protocol",
    name: "Ocean Protocol",
    symbol: "OCEAN",
    price: 0.85,
    change1h: 1.2,
    change24h: 8.5,
    change7d: 25.4,
    volume: 145678901,
    marketCap: 567890123,
    categories: ["ai", "data-marketplace", "ethereum"],
  },
  {
    id: "oasis-network",
    name: "Oasis Network",
    symbol: "ROSE",
    price: 0.12,
    change1h: 0.8,
    change24h: 5.2,
    change7d: 18.6,
    volume: 98765432,
    marketCap: 345678901,
    categories: ["ai", "privacy", "smart-contracts", "layer-1"],
  },
  {
    id: "graph",
    name: "The Graph",
    symbol: "GRT",
    price: 0.45,
    change1h: 1.5,
    change24h: 7.8,
    change7d: 22.3,
    volume: 123456789,
    marketCap: 789012345,
    categories: ["ai", "data-indexing", "ethereum"],
  },
  {
    id: "injective",
    name: "Injective",
    symbol: "INJ",
    price: 32.45,
    change1h: 2.8,
    change24h: 18.5,
    change7d: 42.3,
    volume: 345678901,
    marketCap: 2345678901,
    categories: ["ai", "defi", "cosmos", "layer-1"],
  },
  {
    id: "worldcoin",
    name: "Worldcoin",
    symbol: "WLD",
    price: 5.67,
    change1h: 1.2,
    change24h: 9.5,
    change7d: 28.4,
    volume: 234567890,
    marketCap: 1234567890,
    categories: ["ai", "identity", "optimism"],
  },
  {
    id: "bittensor",
    name: "Bittensor",
    symbol: "TAO",
    price: 485.32,
    change1h: 3.5,
    change24h: 22.5,
    change7d: 55.8,
    volume: 456789012,
    marketCap: 3456789012,
    categories: ["ai", "blockchain-ai", "layer-1"],
  },
  {
    id: "render",
    name: "Render",
    symbol: "RNDR",
    price: 7.85,
    change1h: 1.8,
    change24h: 12.4,
    change7d: 35.6,
    volume: 234567890,
    marketCap: 1567890123,
    categories: ["ai", "gpu-rendering", "ethereum"],
  },
  {
    id: "akash",
    name: "Akash Network",
    symbol: "AKT",
    price: 3.24,
    change1h: 1.5,
    change24h: 8.7,
    change7d: 24.5,
    volume: 123456789,
    marketCap: 789012345,
    categories: ["ai", "cloud-computing", "cosmos"],
  },
  {
    id: "binancecoin",
    name: "BNB",
    symbol: "BNB",
    price: 428.56,
    change1h: 0.18,
    change24h: 2.34,
    change7d: 6.78,
    volume: 2345678901,
    marketCap: 65432109876,
    categories: ["exchange-token", "smart-contracts", "layer-1"],
  },
  {
    id: "cardano",
    name: "Cardano",
    symbol: "ADA",
    price: 0.65,
    change1h: 0.12,
    change24h: 1.45,
    change7d: 3.67,
    volume: 1234567890,
    marketCap: 23456789012,
    categories: ["smart-contracts", "pos", "layer-1"],
  },
  {
    id: "solana",
    name: "Solana",
    symbol: "SOL",
    price: 125.45,
    change1h: 0.45,
    change24h: 3.78,
    change7d: 12.34,
    volume: 3456789012,
    marketCap: 54321098765,
    categories: ["smart-contracts", "pos", "layer-1"],
  }
];

// Helper function to get coins by category
export const getCoinsByCategory = (category) => {
  return coins.filter(coin => coin.categories.includes(category));
};

// Helper function to get trending coins by category (based on 24h change)
export const getTrendingCoinsByCategory = (category, limit = 3) => {
  return getCoinsByCategory(category)
    .sort((a, b) => b.change24h - a.change24h)
    .slice(0, limit);
};

// Helper function to get top coins by category (based on market cap)
export const getTopCoinsByCategory = (category, limit = 3) => {
  return getCoinsByCategory(category)
    .sort((a, b) => b.marketCap - a.marketCap)
    .slice(0, limit);
};

// Helper function to calculate total market cap for a category
export const getCategoryMarketCap = (category) => {
  return getCoinsByCategory(category)
    .reduce((total, coin) => total + coin.marketCap, 0);
};

// Helper function to calculate total volume for a category
export const getCategoryVolume = (category) => {
  return getCoinsByCategory(category)
    .reduce((total, coin) => total + coin.volume, 0);
};

// Trending coins subset for widgets - sorted by highest volume
export const trendingCoins = coins
  .sort((a, b) => b.volume - a.volume)
  .slice(0, 3)
  .map(({ name, symbol, change24h, price }) => ({
    name,
    symbol,
    change24h,
    price,
  })); 