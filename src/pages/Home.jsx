import { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  ArrowUpRight,
  BarChart2,
} from "lucide-react";

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
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          Market Overview
          <span className="bg-gradient-to-r from-teal-500 to-teal-700 text-white text-xs px-2 py-1 rounded-full ml-3">
            LIVE
          </span>
        </h2>

        <div className="grid grid-cols-9 gap-4">
          {/* Trending coins card*/}
          <div className="col-span-2 row-span-2 rounded-xl shadow-md border border-teal-100 hover:shadow-lg transition-all overflow-hidden">
            <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-3 font-medium flex items-center cursor-pointer hover:from-teal-700 hover:to-teal-800 transition-all">
              <TrendingUp size={18} className="mr-2" />
              <span className="flex items-center w-full justify-between">
                Trending Coins
                <ArrowUpRight size={14} />
              </span>
            </div>
            <div className="p-4">
              {trendingCoins.map((coin, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between ${
                    index < trendingCoins.length - 1
                      ? "border-b border-teal-100 pb-3 mb-3"
                      : ""
                  }`}
                >
                  <div className="flex items-center">
                    <div className="h-8 w-8 rounded-full bg-gradient-to-br from-teal-400 to-teal-600 flex items-center justify-center text-white font-bold mr-3 shadow-sm">
                      {coin.symbol.charAt(0)}
                    </div>
                    <div>
                      <div className="font-medium">{coin.name}</div>
                      <div className="text-gray-500 text-xs">{coin.symbol}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">
                      ${coin.price.toLocaleString()}
                    </div>
                    <div
                      className={`text-xs flex items-center justify-end ${
                        coin.change24h >= 0 ? "text-green-500" : "text-red-500"
                      }`}
                    >
                      {coin.change24h >= 0 ? (
                        <TrendingUp size={12} className="mr-1" />
                      ) : (
                        <TrendingDown size={12} className="mr-1" />
                      )}
                      {coin.change24h >= 0 ? "+" : ""}
                      {coin.change24h}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Sectors card */}
          <div className="col-span-2 row-span-2 rounded-xl shadow-md border border-purple-100 hover:shadow-lg transition-all overflow-hidden">
            <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-3 font-medium flex items-center cursor-pointer hover:from-teal-700 hover:to-teal-800 transition-all">
              <BarChart2 size={18} className="mr-2" />
              <span className="flex items-center w-full justify-between">
                Top Sectors
                <ArrowUpRight size={14} />
              </span>
            </div>
            <div className="p-4">
              {topSectors.map((sector, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between ${
                    index < topSectors.length - 1
                      ? "border-b border-purple-100 pb-3 mb-3"
                      : ""
                  }`}
                >
                  <div className="flex items-center">
                    <div className="h-8 w-8 rounded-full bg-gradient-to-br from-teal-400 to-teal-600 flex items-center justify-center text-white font-bold mr-3 shadow-sm">
                      {sector.name.charAt(0)}
                    </div>
                    <div>
                      <div className="font-medium">{sector.name}</div>
                      <div className="text-gray-500 text-xs">
                        Market Cap: {sector.marketCap}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div
                      className={`text-sm flex items-center justify-end ${
                        sector.change >= 0 ? "text-green-500" : "text-red-500"
                      }`}
                    >
                      {sector.change >= 0 ? (
                        <TrendingUp size={12} className="mr-1" />
                      ) : (
                        <TrendingDown size={12} className="mr-1" />
                      )}
                      {sector.change >= 0 ? "+" : ""}
                      {sector.change}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
