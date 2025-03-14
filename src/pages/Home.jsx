import { useState } from "react";
import { coins, trendingCoins } from "../data/coins";
import { topSectors } from "../data/sectors";
import {
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Bitcoin,
  Activity,
  Zap,
  DollarSign,
  ArrowUpRight,
  BarChart2,
  Coins,
  Globe,
  Rocket,
  Star,
  ChartNoAxesColumnIncreasing,
  ArrowUp,
  ArrowDown,
} from "lucide-react";

const Home = () => {
  const [activeTab, setActiveTab] = useState("top");
  const [sortConfig, setSortConfig] = useState({
    key: "marketCap",
    direction: "desc",
  });

  // Get market cap ranking map
  const getMarketCapRanking = () => {
    const sortedByMarketCap = [...coins].sort(
      (a, b) => b.marketCap - a.marketCap
    );
    return new Map(
      sortedByMarketCap.map((coin, index) => [coin.id, index + 1])
    );
  };

  // Handle sorting
  const handleSort = (key) => {
    setSortConfig((prevConfig) => ({
      key,
      direction:
        prevConfig.key === key && prevConfig.direction === "desc"
          ? "asc"
          : "desc",
    }));
  };

  // Get sorted data
  const getSortedCoins = () => {
    const filteredCoins = getFilteredCoins();
    const marketCapRanking = getMarketCapRanking();

    return [...filteredCoins].sort((a, b) => {
      if (sortConfig.key === "#") {
        const aRank = marketCapRanking.get(a.id);
        const bRank = marketCapRanking.get(b.id);
        return sortConfig.direction === "desc" ? aRank - bRank : bRank - aRank;
      }

      let aValue =
        sortConfig.key === "coin" ? a.name.toLowerCase() : a[sortConfig.key];
      let bValue =
        sortConfig.key === "coin" ? b.name.toLowerCase() : b[sortConfig.key];

      if (sortConfig.direction === "asc") {
        return aValue > bValue ? 1 : -1;
      }
      return aValue < bValue ? 1 : -1;
    });
  };

  // Sample chart data - would be replaced with real data
  const marketCapChartData = [1.72, 1.73, 1.71, 1.75, 1.77, 1.76, 1.79, 1.78];

  const volumeChartData = [71.2, 74.3, 72.1, 75.5, 83.1, 81.2, 77.5, 78.4];

  const generateLineChart = (data, isPositive) => {
    const width = 80;
    const height = 40;
    const padding = 5;

    const maxValue = Math.max(...data);
    const minValue = Math.min(...data);

    // Scale data points to fit in the given height
    const scaledData = data.map((value) => {
      const range = maxValue - minValue;
      if (range === 0) return padding;
      return (
        height - padding - ((value - minValue) / range) * (height - padding * 2)
      );
    });

    // Create the path string
    const pathString = scaledData
      .map((point, index) => {
        const x = (index / (data.length - 1)) * width;
        return `${index === 0 ? "M" : "L"} ${x} ${point}`;
      })
      .join(" ");

    return (
      <svg width={width} height={height} className="ml-2">
        <path
          d={pathString}
          stroke={isPositive ? "#10b981" : "#ef4444"}
          strokeWidth="2"
          fill="none"
        />

        <path
          d={`${pathString} L ${width} ${height} L 0 ${height} Z`}
          fill={
            isPositive ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)"
          }
        />
      </svg>
    );
  };

  // Filter data based on active tab
  const getFilteredCoins = () => {
    switch (activeTab) {
      case "top":
        return [...coins].sort((a, b) => b.marketCap - a.marketCap);
      case "trending":
        return [...coins].sort((a, b) => b.volume - a.volume);
      case "gainers":
        return [...coins].sort((a, b) => b.change24h - a.change24h);
      case "losers":
        return [...coins].sort((a, b) => a.change24h - b.change24h);
      default:
        return coins;
    }
  };

  // Generate sparkline-like trend indicator
  const getTrendIndicator = (value) => {
    const width = 160;
    const height = 70;
    const padding = 5;

    // Generate random data points for a more dynamic look
    const data = Array.from({ length: 16 }, () => {
      const base = value > 0 ? 20 : 60;
      return base + (Math.random() * 20 - 10);
    });

    const maxValue = Math.max(...data);
    const minValue = Math.min(...data);

    // Scale data points to fit
    const scaledData = data.map((value) => {
      const range = maxValue - minValue;
      if (range === 0) return padding;
      return (
        height - padding - ((value - minValue) / range) * (height - padding * 2)
      );
    });

    // Create the path string
    const pathString = scaledData
      .map((point, index) => {
        const x = (index / (data.length - 1)) * width;
        return `${index === 0 ? "M" : "L"} ${x} ${point}`;
      })
      .join(" ");

    return (
      <svg width={width} height={height} className="ml-2">
        <path
          d={pathString}
          stroke={value > 0 ? "#10b981" : "#ef4444"}
          strokeWidth="2"
          fill="none"
        />
      </svg>
    );
  };

  // Format large numbers with commas
  const formatNumber = (num) => {
    return num.toLocaleString();
  };

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
                      ? "border-b border-teal-100 pb-4 mb-4"
                      : ""
                  }`}
                >
                  <div className="flex items-center">
                    <div className="h-8 w-8 rounded-full bg-gradient-to-br from-teal-400 to-teal-600 flex items-center justify-center text-white font-bold mr-3 shadow-sm">
                      {coin.symbol.charAt(0)}
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="font-medium">{coin.name}</div>
                      <div className="text-gray-500 text-sm">
                        ({coin.symbol})
                      </div>
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
                      ? "border-b border-purple-100 pb-4 mb-4"
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

          {/* Total Market Cap card */}
          <div className="col-span-2 h-32 rounded-xl shadow-md border border-teal-100 hover:shadow-lg transition-all overflow-hidden">
            <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-3 font-medium flex items-center cursor-pointer hover:from-teal-700 hover:to-teal-800 transition-all">
              <DollarSign size={18} className="mr-2" />
              <span className="flex items-center w-full justify-between">
                Total Market Cap
                <ArrowUpRight size={14} />
              </span>
            </div>

            <div className="p-4 pt-7 flex items-center h-16">
              {/* Price and change on the left */}
              <div className="flex-grow flex flex-col items-start">
                <div className="font-medium text-lg">$1,780,000,000,000</div>
                <div className="text-sm text-green-500 flex items-center">
                  <ArrowUpRight size={14} className="mr-1" /> +2.3% (24h)
                </div>
              </div>
              {/* Line chart on the right */}
              <div className="flex-none">
                {generateLineChart(marketCapChartData, true)}
              </div>
            </div>
          </div>

          {/* BTC Dominance */}
          <div className="col-span-1 h-32 bg-gradient-to-br from-yellow-50 to-yellow-100 p-3 rounded-xl shadow-md border border-yellow-100 hover:shadow-lg transition-all">
            <div className="flex flex-col items-center text-center h-full justify-between py-1">
              <div className="p-2 bg-yellow-500 text-white rounded-lg">
                <Bitcoin size={16} />
              </div>
              <div className="text-gray-500 text-xs font-medium">
                BTC Dominance
              </div>
              <div className="text-lg font-bold">48.2%</div>
              <div className="text-xs text-red-500">-0.4%</div>
            </div>
          </div>

          {/* Fear & Greed */}
          <div className="col-span-1 h-32 bg-gradient-to-br from-green-50 to-green-100 p-3 rounded-xl shadow-md border border-green-100 hover:shadow-lg transition-all">
            <div className="flex flex-col items-center text-center h-full justify-between py-1">
              <div className="p-2 bg-green-500 text-white rounded-lg">
                <AlertCircle size={16} />
              </div>
              <div className="text-gray-500 text-xs font-medium">
                Fear & Greed
              </div>
              <div className="text-lg font-bold">72</div>
              <div className="text-xs text-green-500">Greedy</div>
            </div>
          </div>

          {/* Active Coins */}
          <div className="col-span-1 h-32 bg-gradient-to-br from-purple-50 to-purple-100 p-3 rounded-xl shadow-md border border-purple-100 hover:shadow-lg transition-all">
            <div className="flex flex-col items-center text-center h-full justify-between py-1">
              <div className="p-2 bg-purple-500 text-white rounded-lg">
                <Coins size={16} />
              </div>
              <div className="text-gray-500 text-xs font-medium">Coins</div>
              <div className="text-lg font-bold">1.2M</div>
              <div className="text-xs text-green-500">+5.7%</div>
            </div>
          </div>

          {/* 24h Trading Volume */}
          <div className="col-span-2 h-32 rounded-xl shadow-md border border-teal-100 hover:shadow-lg transition-all overflow-hidden">
            <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-3 font-medium flex items-center cursor-pointer hover:from-teal-700 hover:to-teal-800 transition-all">
              <Activity size={18} className="mr-2" />
              <span className="flex items-center w-full justify-between">
                24h Trading Volume
                <ArrowUpRight size={14} />
              </span>
            </div>
            <div className="p-4 pt-7 flex items-center h-16">
              {/* Price and change on the left */}
              <div className="flex-grow flex flex-col items-start">
                <div className="font-medium text-lg">$78,400,000,000</div>
                <div className="text-sm text-red-500 flex items-center">
                  <TrendingDown size={14} className="mr-1" /> -4.7% (24h)
                </div>
              </div>

              {/* Line chart on the right */}
              <div className="flex-none">
                {generateLineChart(volumeChartData, false)}
              </div>
            </div>
          </div>

          {/* ETH Gas */}
          <div className="col-span-1 h-32 bg-gradient-to-br from-cyan-50 to-cyan-100 p-3 rounded-xl shadow-md border border-cyan-100 hover:shadow-lg transition-all">
            <div className="flex flex-col items-center text-center h-full justify-between py-1">
              <div className="p-2 bg-cyan-500 text-white rounded-lg">
                <Zap size={16} />
              </div>
              <div className="text-gray-500 text-xs font-medium">ETH Gwei</div>
              <div className="text-lg font-bold">24</div>
              <div className="text-xs text-green-500">Low</div>
            </div>
          </div>

          {/* Altcoin Season Index */}
          <div className="col-span-1 h-32 bg-gradient-to-br from-red-50 to-red-100 p-3 rounded-xl shadow-md border border-purple-100 hover:shadow-lg transition-all">
            <div className="flex flex-col items-center text-center h-full justify-between py-1">
              <div className="p-2 bg-red-500 text-white rounded-lg">
                <Rocket size={16} />
              </div>
              <div className="text-gray-500 text-xs font-medium">
                Altcoin Season Index
              </div>
              <div className="text-lg font-bold">68</div>
              <div className="text-xs text-orange-500">Almost There!</div>
            </div>
          </div>

          {/* Global Exchanges */}
          <div className="col-span-1 h-32 bg-gradient-to-br from-blue-50 to-blue-100 p-3 rounded-xl shadow-md border border-blue-100 hover:shadow-lg transition-all">
            <div className="flex flex-col items-center text-center h-full justify-between py-1">
              <div className="p-2 bg-blue-500 text-white rounded-lg">
                <Globe size={16} />
              </div>
              <div className="text-gray-500 text-xs font-medium">Exchanges</div>
              <div className="text-lg font-bold">312</div>
              <div className="text-xs text-red-500">-2</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main heading */}
      <h2 className="text-2xl font-bold mb-4">
        Cryptocurrency Prices by Market Cap
      </h2>

      {/* Tabs */}
      <div className="flex mb-4 p-1 rounded-full w-fit">
        {[
          {
            id: "top",
            label: "Top",
            icon: <ChartNoAxesColumnIncreasing size={16} />,
          },
          {
            id: "trending",
            label: "Trending",
            icon: <Activity size={16} />,
          },
          {
            id: "gainers",
            label: "Top Gainers",
            icon: <TrendingUp size={16} />,
          },
          {
            id: "losers",
            label: "Top Losers",
            icon: <TrendingDown size={16} />,
          },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center px-4 py-2 rounded-full text-sm transition-all cursor-pointer font-semibold ${
              activeTab === tab.id
                ? "bg-teal-100 text-teal-700"
                : "text-gray-500 hover:bg-gray-200"
            }`}
          >
            <span
              className={`mr-2 ${
                activeTab === tab.id ? "text-teal-700" : "text-gray-500"
              }`}
            >
              {tab.icon}
            </span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Main coin list */}
      <div className="overflow-hidden rounded-xl">
        <table className="min-w-full">
          <thead className="bg-gradient-to-r from-teal-600 to-teal-700">
            <tr>
              <th className="py-4 text-left text-xs font-medium text-white uppercase tracking-wider"></th>
              <th className="py-4 pl-5 text-left text-xs font-medium text-white uppercase tracking-wider">
                <div className="flex items-center gap-1">
                  <span className="text-white">#</span>
                </div>
              </th>
              <th className="py-4 pl-7 text-left text-xs font-medium text-white uppercase tracking-wider">
                <div className="flex items-center gap-1">
                  <span
                    className="cursor-pointer hover:text-teal-200 transition-colors"
                    onClick={() => handleSort("coin")}
                  >
                    Coin
                  </span>
                  {sortConfig.key === "coin" &&
                    (sortConfig.direction === "desc" ? (
                      <ArrowDown size={14} />
                    ) : (
                      <ArrowUp size={14} />
                    ))}
                </div>
              </th>
              <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider">
                <div className="flex items-center justify-end gap-1">
                  {sortConfig.key === "price" &&
                    (sortConfig.direction === "desc" ? (
                      <ArrowDown size={14} />
                    ) : (
                      <ArrowUp size={14} />
                    ))}
                  <span
                    className="cursor-pointer hover:text-teal-200 transition-colors"
                    onClick={() => handleSort("price")}
                  >
                    Price
                  </span>
                </div>
              </th>
              <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider">
                <div className="flex items-center justify-end gap-1">
                  {sortConfig.key === "change1h" &&
                    (sortConfig.direction === "desc" ? (
                      <ArrowDown size={14} />
                    ) : (
                      <ArrowUp size={14} />
                    ))}
                  <span
                    className="cursor-pointer hover:text-teal-200 transition-colors"
                    onClick={() => handleSort("change1h")}
                  >
                    1h
                  </span>
                </div>
              </th>
              <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider">
                <div className="flex items-center justify-end gap-1">
                  {sortConfig.key === "change24h" &&
                    (sortConfig.direction === "desc" ? (
                      <ArrowDown size={14} />
                    ) : (
                      <ArrowUp size={14} />
                    ))}
                  <span
                    className="cursor-pointer hover:text-teal-200 transition-colors"
                    onClick={() => handleSort("change24h")}
                  >
                    24h
                  </span>
                </div>
              </th>
              <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider">
                <div className="flex items-center justify-end gap-1">
                  {sortConfig.key === "change7d" &&
                    (sortConfig.direction === "desc" ? (
                      <ArrowDown size={14} />
                    ) : (
                      <ArrowUp size={14} />
                    ))}
                  <span
                    className="cursor-pointer hover:text-teal-200 transition-colors"
                    onClick={() => handleSort("change7d")}
                  >
                    7d
                  </span>
                </div>
              </th>
              <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider">
                <div className="flex items-center justify-end gap-1">
                  {sortConfig.key === "volume" &&
                    (sortConfig.direction === "desc" ? (
                      <ArrowDown size={14} />
                    ) : (
                      <ArrowUp size={14} />
                    ))}
                  <span
                    className="cursor-pointer hover:text-teal-200 transition-colors"
                    onClick={() => handleSort("volume")}
                  >
                    Volume 24h
                  </span>
                </div>
              </th>
              <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider">
                <div className="flex items-center justify-end gap-1">
                  {sortConfig.key === "marketCap" &&
                    (sortConfig.direction === "desc" ? (
                      <ArrowDown size={14} />
                    ) : (
                      <ArrowUp size={14} />
                    ))}
                  <span
                    className="cursor-pointer hover:text-teal-200 transition-colors"
                    onClick={() => handleSort("marketCap")}
                  >
                    Market Cap
                  </span>
                </div>
              </th>
              <th className="py-4 pr-5 text-right text-xs font-medium text-white uppercase tracking-wider">
                Last 7 Days
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {getSortedCoins().map((coin) => {
              const marketCapRanking = getMarketCapRanking();
              return (
                <tr
                  key={coin.id}
                  className="hover:bg-teal-50 transition-colors cursor-pointer"
                >
                  <td className="py-4 pl-3 whitespace-nowrap text-sm font-medium text-gray-700 w-0">
                    <Star
                      size={16}
                      className="text-gray-400 hover:text-yellow-500"
                    />
                  </td>
                  <td className="py-4 pl-5 whitespace-nowrap text-sm font-medium text-gray-700 w-0">
                    {marketCapRanking.get(coin.id)}
                  </td>
                  <td className="py-4 pl-7 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-8 w-8 rounded-full bg-gradient-to-br from-teal-400 to-teal-600 flex items-center justify-center text-white font-bold mr-3 shadow-md">
                        {coin.symbol.charAt(0)}
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="font-medium">{coin.name}</div>
                        <div className="text-gray-500 text-sm">
                          {coin.symbol}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 text-right whitespace-nowrap font-medium w-0">
                    ${coin.price.toLocaleString()}
                  </td>
                  <td
                    className={`py-4 pl-5 text-right whitespace-nowrap w-0 font-medium ${
                      coin.change1h >= 0 ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    <span className="flex items-center justify-end">
                      {coin.change1h >= 0 ? (
                        <TrendingUp size={14} className="mr-1" />
                      ) : (
                        <TrendingDown size={14} className="mr-1" />
                      )}
                      {coin.change1h >= 0 ? "+" : ""}
                      {coin.change1h}%
                    </span>
                  </td>
                  <td
                    className={`py-4 pl-5 text-right whitespace-nowrap w-0 font-medium ${
                      coin.change24h >= 0 ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    <span className="flex items-center justify-end">
                      {coin.change24h >= 0 ? (
                        <TrendingUp size={14} className="mr-1" />
                      ) : (
                        <TrendingDown size={14} className="mr-1" />
                      )}
                      {coin.change24h >= 0 ? "+" : ""}
                      {coin.change24h}%
                    </span>
                  </td>
                  <td
                    className={`py-4 pl-5 text-right whitespace-nowrap w-0 font-medium ${
                      coin.change7d >= 0 ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    <span className="flex items-center justify-end">
                      {coin.change7d >= 0 ? (
                        <TrendingUp size={14} className="mr-1" />
                      ) : (
                        <TrendingDown size={14} className="mr-1" />
                      )}
                      {coin.change7d >= 0 ? "+" : ""}
                      {coin.change7d}%
                    </span>
                  </td>
                  <td className="py-4 pl-5 text-right whitespace-nowrap w-0">
                    ${formatNumber(coin.volume)}
                  </td>
                  <td className="py-4 pl-4 text-right whitespace-nowrap w-0">
                    ${formatNumber(coin.marketCap)}
                  </td>
                  <td className="pr-4 pl-4 text-right w-0">
                    <div className="rounded-md p-1 flex justify-end">
                      {getTrendIndicator(coin.change7d)}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Home;
