import { useState } from "react";
import { coins } from "../../data/coins";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  DollarSign,
  Star,
  ChartNoAxesColumnIncreasing,
  ArrowUp,
  ArrowDown,
  Search,
  Coins,
  Zap,
  Globe,
  Blocks,
  Boxes,
  Wallet,
  Brain,
  Gamepad2,
  Link2,
  Building2,
  Rocket,
  Gem,
} from "lucide-react";
import { Link } from "react-router-dom";

const AiCoins = () => {
  const [activeTab, setActiveTab] = useState("top");
  const [sortConfig, setSortConfig] = useState({
    key: "marketCap",
    direction: "desc",
  });
  const [searchQuery, setSearchQuery] = useState("");

  // Get active tab position and width
  const getTabStyle = () => {
    const tabsContainer = document.querySelector("[data-tabs-container]");
    if (!tabsContainer) return { width: "16.7%", transform: "translateX(0)" };

    const activeTabElement = tabsContainer.querySelector(
      `[data-tab-id="${activeTab}"]`
    );
    if (!activeTabElement)
      return { width: "16.7%", transform: "translateX(0)" };

    const containerLeft = tabsContainer.getBoundingClientRect().left;
    const tabLeft = activeTabElement.getBoundingClientRect().left;
    const tabWidth = activeTabElement.getBoundingClientRect().width;

    return {
      width: `${tabWidth}px`,
      transform: `translateX(${tabLeft - containerLeft}px)`,
    };
  };

  // Filter AI coins
  const aiCoins = coins.filter((coin) => coin.categories.includes("ai"));

  // Get market cap ranking map
  const getMarketCapRanking = () => {
    const sortedByMarketCap = [...aiCoins].sort(
      (a, b) => b.marketCap - a.marketCap
    );
    return new Map(
      sortedByMarketCap.map((coin, index) => [coin.id, index + 1])
    );
  };

  // Calculate total market cap and volume
  const totalMarketCap = aiCoins.reduce((sum, coin) => sum + coin.marketCap, 0);
  const totalVolume = aiCoins.reduce((sum, coin) => sum + coin.volume, 0);

  // Get trending AI coins
  const trendingAiCoins = [...aiCoins]
    .sort((a, b) => b.change24h - a.change24h)
    .slice(0, 3);

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

  // Get sorted and filtered coins
  const getSortedCoins = () => {
    let filteredCoins = [...aiCoins];

    // Apply search filter
    if (searchQuery) {
      filteredCoins = filteredCoins.filter(
        (coin) =>
          coin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          coin.symbol.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply tab filter
    switch (activeTab) {
      case "top":
        filteredCoins.sort((a, b) => b.marketCap - a.marketCap);
        break;
      case "trending":
        filteredCoins.sort((a, b) => b.volume - a.volume);
        break;
      case "gainers":
        filteredCoins.sort((a, b) => b.change24h - a.change24h);
        break;
      case "losers":
        filteredCoins.sort((a, b) => a.change24h - b.change24h);
        break;
      default:
        break;
    }

    // Apply column sorting
    if (sortConfig.key) {
      filteredCoins.sort((a, b) => {
        if (sortConfig.key === "#") {
          const marketCapRanking = getMarketCapRanking();
          const aRank = marketCapRanking.get(a.id);
          const bRank = marketCapRanking.get(b.id);
          return sortConfig.direction === "desc"
            ? aRank - bRank
            : bRank - aRank;
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
    }

    return filteredCoins;
  };

  // Generate trend indicator
  const getTrendIndicator = (value) => {
    const width = 160;
    const height = 70;
    const padding = 5;

    const data = Array.from({ length: 16 }, () => {
      const base = value > 0 ? 20 : 60;
      return base + (Math.random() * 20 - 10);
    });

    const maxValue = Math.max(...data);
    const minValue = Math.min(...data);

    const scaledData = data.map((value) => {
      const range = maxValue - minValue;
      if (range === 0) return padding;
      return (
        height - padding - ((value - minValue) / range) * (height - padding * 2)
      );
    });

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

  // Format large numbers
  const formatNumber = (num, fullNumber = false) => {
    if (fullNumber) {
      if (num >= 1e12) return (num / 1e12).toFixed(2) + "T";
      if (num >= 1e9) return (num / 1e9).toFixed(2) + "B";
      if (num >= 1e6) return (num / 1e6).toFixed(2) + "M";
      return num.toLocaleString();
    } else {
      return "$" + num.toLocaleString();
    }
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          Market Overview
          <span className="bg-gradient-to-r from-purple-500 to-purple-700 text-white text-xs px-2 py-1 rounded-full ml-3">
            LIVE
          </span>
        </h2>

        <div className="grid grid-cols-3 gap-4 mb-6">
          {/* Total Market Cap card */}
          <div className="rounded-xl shadow-md border border-purple-100 hover:shadow-lg transition-all overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white p-3 font-medium flex items-center">
              <DollarSign size={18} className="mr-2" />
              <span>Total AI Market Cap</span>
            </div>
            <div className="p-4">
              <div className="text-2xl font-bold mb-2">
                ${formatNumber(totalMarketCap, true)}
              </div>
              <div className="text-purple-600 text-sm">
                {aiCoins.length} Active AI Coins
              </div>
            </div>
          </div>

          {/* 24h Volume card */}
          <div className="rounded-xl shadow-md border border-purple-100 hover:shadow-lg transition-all overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white p-3 font-medium flex items-center">
              <Activity size={18} className="mr-2" />
              <span>24h Trading Volume</span>
            </div>
            <div className="p-4">
              <div className="text-2xl font-bold mb-2">
                ${formatNumber(totalVolume, true)}
              </div>
              <div className="text-purple-600 text-sm">
                Across all AI tokens
              </div>
            </div>
          </div>

          {/* Trending AI coins card */}
          <div className="rounded-xl shadow-md border border-purple-100 hover:shadow-lg transition-all overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white p-3 font-medium flex items-center">
              <TrendingUp size={18} className="mr-2" />
              <span>Top Trending AI Coins</span>
            </div>
            <div className="p-4">
              {trendingAiCoins.map((coin, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between mb-2"
                >
                  <div className="flex items-center">
                    <div className="font-medium">{coin.symbol}</div>
                  </div>
                  <div
                    className={`${
                      coin.change24h >= 0 ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    {coin.change24h >= 0 ? "+" : ""}
                    {coin.change24h}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main heading */}
        <h2 className="text-2xl font-bold mb-4">
          AI Cryptocurrency Prices by Market Cap
        </h2>

        {/* Tabs */}
        <div
          className="flex mb-2 rounded-full w-fit bg-gray-100/80 backdrop-blur-sm relative"
          data-tabs-container
        >
          <div
            className="absolute h-full w-full rounded-full bg-gradient-to-r from-purple-600 to-purple-700 transition-all duration-300 ease-in-out"
            style={getTabStyle()}
          />
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
              data-tab-id={tab.id}
              onClick={() => {
                setActiveTab(tab.id);
                setSortConfig({});
              }}
              className={`relative z-10 flex items-center px-4 py-2 rounded-full text-sm transition-all duration-300 ease-in-out cursor-pointer font-semibold ${
                activeTab === tab.id
                  ? "text-white"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              <span
                className={`${
                  tab.id === "top" ? "mr-1" : "mr-2"
                } transition-colors duration-300 ${
                  activeTab === tab.id ? "text-white" : "text-gray-500"
                }`}
              >
                {tab.icon}
              </span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Categories and Search container */}
        <div className="flex items-center justify-between mb-2">
          {/* Category tabs */}
          <div className="flex flex-wrap gap-1 p-1 w-fit">
            {[
              {
                id: "bnb",
                label: "BNB",
                icon: <Coins size={14} />,
                path: "/category/bnb",
              },
              {
                id: "sol",
                label: "SOL",
                icon: <Zap size={14} />,
                path: "/category/sol",
              },
              {
                id: "dot",
                label: "DOT",
                icon: <Globe size={14} />,
                path: "/category/dot",
              },
              {
                id: "smart-contract",
                label: "Smart Contract",
                icon: <Blocks size={14} />,
                path: "/category/smart-contract",
              },
              {
                id: "layer1",
                label: "Layer 1",
                icon: <Blocks size={14} />,
                path: "/category/layer-1",
              },
              {
                id: "layer2",
                label: "Layer 2",
                icon: <Boxes size={14} />,
                path: "/category/layer-2",
              },
              {
                id: "defi",
                label: "DeFi",
                icon: <Wallet size={14} />,
                path: "/category/defi",
              },
              {
                id: "ai",
                label: "AI",
                icon: <Brain size={14} />,
                path: "/category/ai",
              },
              {
                id: "gaming",
                label: "Gaming",
                icon: <Gamepad2 size={14} />,
                path: "/category/gaming",
              },
              {
                id: "infrastructure",
                label: "Infrastructure",
                icon: <Link2 size={14} />,
                path: "/category/infrastructure",
              },
              {
                id: "rwa",
                label: "RWA",
                icon: <Building2 size={14} />,
                path: "/category/rwa",
              },
              {
                id: "meme",
                label: "Meme",
                icon: <Rocket size={14} />,
                path: "/category/meme",
              },
              {
                id: "nft",
                label: "NFT",
                icon: <Gem size={14} />,
                path: "/category/nft",
              },
            ].map((category) => (
              <Link
                key={category.id}
                to={category.path}
                className={`flex items-center px-3 py-1.5 rounded-full text-xs transition-all cursor-pointer font-medium
                  ${
                    category.id === "ai"
                      ? "bg-purple-100 text-purple-700"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
              >
                <span
                  className={`mr-1.5 ${
                    category.id === "ai" ? "text-purple-600" : "text-gray-500"
                  }`}
                >
                  {category.icon}
                </span>
                {category.label}
              </Link>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search AI coins..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-1.5 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
            />
            <Search
              size={16}
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
            />
          </div>
        </div>

        {/* Main coin list */}
        <div className="overflow-hidden rounded-xl">
          <table className="min-w-full table-fixed">
            <thead className="bg-gradient-to-r from-purple-600 to-purple-700">
              <tr>
                <th className="py-4 pl-3 whitespace-nowrap text-sm font-medium text-white w-0"></th>
                <th className="py-4 pl-5 text-left text-xs font-medium text-white uppercase tracking-wider w-0">
                  <div className="flex items-center gap-1">
                    <span className="text-white">#</span>
                  </div>
                </th>
                <th className="py-4 pl-7 text-left text-xs font-medium text-white uppercase tracking-wider">
                  <div className="flex items-center gap-1">
                    <span
                      className="cursor-pointer hover:text-purple-200 transition-colors"
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
                <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
                  <div className="flex items-center justify-end gap-1">
                    {sortConfig.key === "price" &&
                      (sortConfig.direction === "desc" ? (
                        <ArrowDown size={14} />
                      ) : (
                        <ArrowUp size={14} />
                      ))}
                    <span
                      className="cursor-pointer hover:text-purple-200 transition-colors"
                      onClick={() => handleSort("price")}
                    >
                      Price
                    </span>
                  </div>
                </th>
                <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
                  <div className="flex items-center justify-end gap-1">
                    {sortConfig.key === "change1h" &&
                      (sortConfig.direction === "desc" ? (
                        <ArrowDown size={14} />
                      ) : (
                        <ArrowUp size={14} />
                      ))}
                    <span
                      className="cursor-pointer hover:text-purple-200 transition-colors"
                      onClick={() => handleSort("change1h")}
                    >
                      1h
                    </span>
                  </div>
                </th>
                <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
                  <div className="flex items-center justify-end gap-1">
                    {sortConfig.key === "change24h" &&
                      (sortConfig.direction === "desc" ? (
                        <ArrowDown size={14} />
                      ) : (
                        <ArrowUp size={14} />
                      ))}
                    <span
                      className="cursor-pointer hover:text-purple-200 transition-colors"
                      onClick={() => handleSort("change24h")}
                    >
                      24h
                    </span>
                  </div>
                </th>
                <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
                  <div className="flex items-center justify-end gap-1">
                    {sortConfig.key === "change7d" &&
                      (sortConfig.direction === "desc" ? (
                        <ArrowDown size={14} />
                      ) : (
                        <ArrowUp size={14} />
                      ))}
                    <span
                      className="cursor-pointer hover:text-purple-200 transition-colors"
                      onClick={() => handleSort("change7d")}
                    >
                      7d
                    </span>
                  </div>
                </th>
                <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
                  <div className="flex items-center justify-end gap-1">
                    {sortConfig.key === "volume" &&
                      (sortConfig.direction === "desc" ? (
                        <ArrowDown size={14} />
                      ) : (
                        <ArrowUp size={14} />
                      ))}
                    <span
                      className="cursor-pointer hover:text-purple-200 transition-colors"
                      onClick={() => handleSort("volume")}
                    >
                      Volume 24h
                    </span>
                  </div>
                </th>
                <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
                  <div className="flex items-center justify-end gap-1">
                    {sortConfig.key === "marketCap" &&
                      (sortConfig.direction === "desc" ? (
                        <ArrowDown size={14} />
                      ) : (
                        <ArrowUp size={14} />
                      ))}
                    <span
                      className="cursor-pointer hover:text-purple-200 transition-colors"
                      onClick={() => handleSort("marketCap")}
                    >
                      Market Cap
                    </span>
                  </div>
                </th>
                <th className="py-4 pr-5 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
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
                    className="hover:bg-purple-50 transition-colors cursor-pointer"
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
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center text-white font-bold mr-3 shadow-md">
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
                      className={`py-4 pl-6 text-right whitespace-nowrap w-0 font-medium ${
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
                      className={`py-4 pl-6 text-right whitespace-nowrap w-0 font-medium ${
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
                      className={`py-4 pl-6 text-right whitespace-nowrap w-0 font-medium ${
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
                    <td className="py-4 pl-9 text-right whitespace-nowrap w-0">
                      {formatNumber(coin.volume)}
                    </td>
                    <td className="py-4 pl-9 text-right whitespace-nowrap w-0">
                      {formatNumber(coin.marketCap)}
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
    </div>
  );
};

export default AiCoins;
