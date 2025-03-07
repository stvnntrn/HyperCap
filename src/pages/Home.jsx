import { useState } from "react";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";

const Home = () => {
  const [activeTab, setActiveTab] = useState("trending");

  // Sample data - would be replaced with real API data
  const coins = [
    {
      id: 1,
      name: "Bitcoin",
      symbol: "BTC",
      price: 48243.21,
      change1h: 0.5,
      change24h: -2.1,
      change7d: 3.8,
      volume: 28432156789,
      marketCap: 893421567890,
    },
    {
      id: 2,
      name: "Ethereum",
      symbol: "ETH",
      price: 2976.45,
      change1h: -0.2,
      change24h: 1.7,
      change7d: -1.3,
      volume: 15678923456,
      marketCap: 352678945123,
    },
    {
      id: 3,
      name: "Solana",
      symbol: "SOL",
      price: 107.32,
      change1h: 1.5,
      change24h: 5.2,
      change7d: 12.4,
      volume: 5678234567,
      marketCap: 42678234567,
    },
    {
      id: 4,
      name: "Ripple",
      symbol: "XRP",
      price: 0.54,
      change1h: 0.1,
      change24h: -0.8,
      change7d: -2.5,
      volume: 2345678912,
      marketCap: 27456789123,
    },
    {
      id: 5,
      name: "Cardano",
      symbol: "ADA",
      price: 0.48,
      change1h: -0.4,
      change24h: 3.2,
      change7d: 8.9,
      volume: 1987654321,
      marketCap: 16789123456,
    },
  ];

  // Trending coins for the widget
  const trendingCoins = [
    { name: "Solana", symbol: "SOL", change24h: 5.2, price: 107.32 },
    { name: "Cardano", symbol: "ADA", change24h: 3.2, price: 0.48 },
    { name: "Ethereum", symbol: "ETH", change24h: 1.7, price: 2976.45 },
  ];

  // Top sectors data
  const topSectors = [
    { name: "GameFi", change: 15.3, marketCap: "48.2B" },
    { name: "Layer 2", change: 9.7, marketCap: "62.5B" },
    { name: "DeFi", change: 7.2, marketCap: "91.3B" },
  ];

  // Sample chart data - would be replaced with real data
  const marketCapChartData = [1.72, 1.73, 1.71, 1.75, 1.77, 1.76, 1.79, 1.78];

  const volumeChartData = [71.2, 74.3, 72.1, 75.5, 83.1, 81.2, 77.5, 78.4];

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <h2 className="text-2xl font-bold mb-6">Cryptocurrency Market</h2>
    </div>
  );
};

export default Home;
