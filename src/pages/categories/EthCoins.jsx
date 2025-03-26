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
  ArrowUpRight,
  PlusCircle,
} from "lucide-react";
import { Link } from "react-router-dom";

const EthCoins = () => {
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

  // Filter ETH coins
  const ethCoins = coins.filter((coin) => coin.categories.includes("eth"));

  // Get market cap ranking map
  const getMarketCapRanking = () => {
    const sortedByMarketCap = [...ethCoins].sort(
      (a, b) => b.marketCap - a.marketCap
    );
    return new Map(
      sortedByMarketCap.map((coin, index) => [coin.id, index + 1])
    );
  };

  // Calculate total market cap and volume
  const totalMarketCap = ethCoins.reduce(
    (sum, coin) => sum + coin.marketCap,
    0
  );
  const totalVolume = ethCoins.reduce((sum, coin) => sum + coin.volume, 0);

  // Get trending ETH coins by volume
  const trendingEthCoins = [...ethCoins]
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 3);

  // Get top gainers
  const topGainers = [...ethCoins]
    .sort((a, b) => b.change24h - a.change24h)
    .slice(0, 3);

  // Get newly listed coins (using market cap as a proxy for listing time)
  const newlyListed = [...ethCoins]
    .sort((a, b) => b.marketCap - a.marketCap)
    .slice(0, 3);

  // Generate sample market cap chart data - now with hourly points
  const marketCapChartData = Array.from({ length: 19 }, (_, i) => {
    const date = new Date();
    date.setHours(date.getHours() + i); // Points every hour
    return {
      value: totalMarketCap * (0.95 + Math.random() * 0.1),
      date: date,
    };
  });

  // Generate sample volume chart data - now with hourly points
  const volumeChartData = Array.from({ length: 19 }, (_, i) => {
    const date = new Date();
    date.setHours(date.getHours() + i); // Points every hour
    return {
      value: totalVolume * (0.95 + Math.random() * 0.1),
      date: date,
    };
  });

  // Generate line chart
  const generateLineChart = (data, isPositive = true) => {
    const width = 1000;
    const height = 120;
    const padding = { top: 20, right: 20, bottom: 30, left: 80 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const values = data.map((d) => d.value);
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);

    // Format large numbers for y-axis
    const formatYAxisValue = (value) => {
      if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
      if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
      if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
      return `$${value.toFixed(0)}`;
    };

    // Format time for x-axis
    const formatTime = (date) => {
      return date.toLocaleTimeString("en-US", {
        hour: "numeric",
        hour12: true,
      });
    };

    // Scale data points
    const scaledData = values.map((value) => {
      const range = maxValue - minValue;
      if (range === 0) return padding.top;
      return (
        height - padding.bottom - ((value - minValue) / range) * chartHeight
      );
    });

    // Generate path
    const pathString = scaledData
      .map((point, index) => {
        const x = padding.left + (index / (data.length - 1)) * chartWidth;
        return `${index === 0 ? "M" : "L"} ${x} ${point}`;
      })
      .join(" ");

    // Calculate y-axis values (3 points)
    const yAxisValues = [
      maxValue,
      minValue + (maxValue - minValue) / 2,
      minValue,
    ];

    return (
      <svg width={width} height={height} className="w-full">
        {/* Y-axis */}
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={height - padding.bottom}
          stroke="#e5e7eb"
          strokeWidth="1"
        />
        {/* X-axis */}
        <line
          x1={padding.left}
          y1={height - padding.bottom}
          x2={width - padding.right}
          y2={height - padding.bottom}
          stroke="#e5e7eb"
          strokeWidth="1"
        />

        {/* Y-axis labels */}
        {yAxisValues.map((value, i) => {
          const y = padding.top + (i * chartHeight) / 2;
          return (
            <g key={i}>
              <line
                x1={padding.left - 5}
                y1={y}
                x2={padding.left}
                y2={y}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
              <text
                x={padding.left - 10}
                y={y}
                textAnchor="end"
                alignmentBaseline="middle"
                className="text-xs text-gray-500"
              >
                {formatYAxisValue(value)}
              </text>
            </g>
          );
        })}

        {/* Hover points */}
        {data.map((point, i) => {
          const x = padding.left + (i / (data.length - 1)) * chartWidth;
          const y = scaledData[i];
          return (
            <g key={`point-${i}`}>
              <circle
                cx={x}
                cy={y}
                r="4"
                className="opacity-0 hover:opacity-100 fill-blue-500 transition-opacity duration-200"
              />
              <g className="opacity-0 hover:opacity-100 transition-opacity duration-200">
                <rect
                  x={x - 50}
                  y={y - 30}
                  width="100"
                  height="20"
                  rx="4"
                  className="fill-gray-800"
                />
                <text
                  x={x}
                  y={y - 16}
                  textAnchor="middle"
                  className="text-xs fill-white"
                >
                  {formatNumber(point.value)}
                </text>
              </g>
            </g>
          );
        })}

        {/* X-axis labels - show only every 6 hours */}
        {data
          .filter((_, i) => i % 6 === 0)
          .map((point, i) => {
            const x = padding.left + ((i * 6) / (data.length - 1)) * chartWidth;
            return (
              <text
                key={i}
                x={x + 15}
                y={height - 8}
                textAnchor="middle"
                className="text-xs text-gray-500 font-medium"
              >
                {formatTime(point.date)}
              </text>
            );
          })}

        {/* Main chart line */}
        <path
          d={pathString}
          stroke={isPositive ? "#10b981" : "#ef4444"}
          strokeWidth="2"
          fill="none"
        />
        <path
          d={`${pathString} L ${width - padding.right} ${
            height - padding.bottom
          } L ${padding.left} ${height - padding.bottom} Z`}
          fill={
            isPositive ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)"
          }
        />
      </svg>
    );
  };

  // Format large numbers
  const formatNumber = (num, fullNumber = false) => {
    if (fullNumber) {
      return num.toLocaleString("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      });
    } else {
      return (
        "$" +
        num.toLocaleString("en-US", {
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        })
      );
    }
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
    let filteredCoins = [...ethCoins];

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

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          ETH Crypto Market Overview
          <span className="bg-gradient-to-r from-gray-400 to-gray-500 text-white text-xs px-2 py-1 rounded-full ml-3">
            LIVE
          </span>
        </h2>

        <div className="grid grid-cols-12 gap-4">
          {/* Market Cap Chart */}
          <div className="col-span-6 rounded-xl shadow-[0_4px_12px_-2px_rgba(0,0,0,0.15)] hover:shadow-[0_6px_16px_-2px_rgba(0,0,0,0.2)] transition-all overflow-hidden bg-white">
            <div className="p-3 font-medium flex items-center justify-between">
              <div className="flex items-center text-gray-500">
                <DollarSign size={18} className="mr-1" />
                <span>Market Cap</span>
              </div>
              <div className="text-green-500 text-sm flex items-center">
                <ArrowUpRight size={14} className="mr-1" />
                +5.2% (24h)
              </div>
            </div>
            <div className="pb-4 pr-4">
              <div className="text-2xl font-bold text-gray-800 pl-4">
                ${(totalMarketCap / 1e9).toFixed(2)}B
              </div>
              <div className="h-[120px]">
                {generateLineChart(marketCapChartData)}
              </div>
            </div>
          </div>

          {/* Volume Chart */}
          <div className="col-span-6 rounded-xl shadow-[0_4px_12px_-2px_rgba(0,0,0,0.15)] hover:shadow-[0_6px_16px_-2px_rgba(0,0,0,0.2)] transition-all overflow-hidden bg-white">
            <div className="p-3 font-medium flex items-center justify-between">
              <div className="flex items-center text-gray-500">
                <Activity size={18} className="mr-2" />
                <span>24h Volume</span>
              </div>
              <div className="text-red-500 text-sm flex items-center">
                <TrendingDown size={14} className="mr-1" />
                -3.8% (24h)
              </div>
            </div>
            <div className="pb-4 pr-4">
              <div className="text-2xl font-bold text-gray-800 pl-4">
                ${(totalVolume / 1e9).toFixed(2)}B
              </div>
              <div className="h-[120px]">
                {generateLineChart(volumeChartData)}
              </div>
            </div>
          </div>

          {/* Trending Coins */}
          <div className="col-span-4 rounded-xl shadow-[0_4px_12px_-2px_rgba(0,0,0,0.15)] hover:shadow-[0_6px_16px_-2px_rgba(0,0,0,0.2)] transition-all overflow-hidden bg-white">
            <div className="text-base text-gray-500 font-medium flex items-center gap-2 px-4 pt-4 pb-2">
              <TrendingUp size={16} />
              Trending
            </div>
            <div className="">
              {trendingEthCoins.map((coin, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between hover:bg-gray-50 transition-colors group px-4 py-3 cursor-pointer"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="h-6 w-6 rounded-full bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-white font-bold text-xs shadow-sm flex-shrink-0">
                      {coin.symbol.charAt(0)}
                    </div>
                    <div className="min-w-0">
                      <div className="font-medium text-sm truncate">
                        {coin.name}
                      </div>
                      <div className="text-gray-500 text-xs">{coin.symbol}</div>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="font-medium text-sm">
                      ${coin.price.toLocaleString()}
                    </div>
                    <div
                      className={`text-xs ${
                        coin.change24h >= 0 ? "text-green-500" : "text-red-500"
                      }`}
                    >
                      {coin.change24h >= 0 ? "+" : ""}
                      {coin.change24h}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Gainers */}
          <div className="col-span-4 rounded-xl shadow-[0_4px_12px_-2px_rgba(0,0,0,0.15)] hover:shadow-[0_6px_16px_-2px_rgba(0,0,0,0.2)] transition-all overflow-hidden bg-white">
            <div className="text-base text-gray-500 font-medium flex items-center gap-2 px-4 pt-4 pb-2">
              <Rocket size={16} />
              Top Gainers
            </div>
            <div className="">
              {topGainers.map((coin, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between hover:bg-gray-50 transition-colors group px-4 py-3 cursor-pointer"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="h-6 w-6 rounded-full bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-white font-bold text-xs shadow-sm flex-shrink-0">
                      {coin.symbol.charAt(0)}
                    </div>
                    <div className="min-w-0">
                      <div className="font-medium text-sm truncate">
                        {coin.name}
                      </div>
                      <div className="text-gray-500 text-xs">{coin.symbol}</div>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="font-medium text-sm">
                      ${coin.price.toLocaleString()}
                    </div>
                    <div className="text-green-500 text-xs">
                      +{coin.change24h}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Newly Listed */}
          <div className="col-span-4 rounded-xl shadow-[0_4px_12px_-2px_rgba(0,0,0,0.15)] hover:shadow-[0_6px_16px_-2px_rgba(0,0,0,0.2)] transition-all overflow-hidden bg-white">
            <div className="text-base text-gray-500 font-medium flex items-center gap-2 px-4 pt-4 pb-2">
              <PlusCircle size={16} />
              Newly Listed
            </div>
            <div className="">
              {newlyListed.map((coin, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between hover:bg-gray-50 transition-colors group px-4 py-3 cursor-pointer"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="h-6 w-6 rounded-full bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-white font-bold text-xs shadow-sm flex-shrink-0">
                      {coin.symbol.charAt(0)}
                    </div>
                    <div className="min-w-0">
                      <div className="font-medium text-sm truncate">
                        {coin.name}
                      </div>
                      <div className="text-gray-500 text-xs">{coin.symbol}</div>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="font-medium text-sm">
                      ${coin.price.toLocaleString()}
                    </div>
                    <div
                      className={`text-xs ${
                        coin.change24h >= 0 ? "text-green-500" : "text-red-500"
                      }`}
                    >
                      {coin.change24h >= 0 ? "+" : ""}
                      {coin.change24h}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main heading */}
        <h2 className="text-2xl font-bold mb-4 mt-8">
          ETH Cryptocurrency Prices by Market Cap
        </h2>

        {/* Tabs */}
        <div
          className="flex mb-2 rounded-full w-fit bg-gray-100/80 backdrop-blur-sm relative"
          data-tabs-container
        >
          <div
            className="absolute h-full w-full rounded-full bg-gradient-to-r from-gray-400 to-gray-500 transition-all duration-300 ease-in-out"
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
                id: "eth",
                label: "ETH",
                icon: <Zap size={14} />,
                path: "/category/eth",
              },
              {
                id: "bnb",
                label: "BNB",
                icon: <Coins size={14} />,
                path: "/category/bnb",
              },
              {
                id: "sol",
                label: "SOL",
                icon: <Globe size={14} />,
                path: "/category/sol",
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
                icon: <Boxes size={14} />,
                path: "/category/layer-1",
              },
              {
                id: "layer2",
                label: "Layer 2",
                icon: <Link2 size={14} />,
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
                icon: <Building2 size={14} />,
                path: "/category/infrastructure",
              },
              {
                id: "rwa",
                label: "RWA",
                icon: <Rocket size={14} />,
                path: "/category/rwa",
              },
              {
                id: "meme",
                label: "Meme",
                icon: <Gem size={14} />,
                path: "/category/meme",
              },
              {
                id: "nft",
                label: "NFT",
                icon: <Activity size={14} />,
                path: "/category/nft",
              },
            ].map((category) => (
              <Link
                key={category.id}
                to={category.path}
                className={`flex items-center px-3 py-1.5 rounded-full text-xs transition-all cursor-pointer font-medium
                  ${
                    category.id === "eth"
                      ? "bg-gray-50 text-gray-500"
                      : "text-gray-400 hover:text-gray-600"
                  }`}
              >
                <span
                  className={`mr-1.5 ${
                    category.id === "eth" ? "text-gray-500" : "text-gray-400"
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
              placeholder="Search ETH coins..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-1.5 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent text-sm"
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
            <thead className="bg-gradient-to-r from-gray-400 to-gray-500">
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
                      className="cursor-pointer hover:text-blue-200 transition-colors"
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
                      className="cursor-pointer hover:text-blue-200 transition-colors"
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
                      className="cursor-pointer hover:text-blue-200 transition-colors"
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
                      className="cursor-pointer hover:text-blue-200 transition-colors"
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
                      className="cursor-pointer hover:text-blue-200 transition-colors"
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
                      className="cursor-pointer hover:text-blue-200 transition-colors"
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
                      className="cursor-pointer hover:text-blue-200 transition-colors"
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
                    className="hover:bg-gray-50/30 transition-colors cursor-pointer"
                  >
                    <td className="py-4 pl-3 whitespace-nowrap text-sm font-medium text-gray-700 w-0">
                      <Star
                        size={16}
                        className="text-gray-400 hover:text-gray-500"
                      />
                    </td>
                    <td className="py-4 pl-5 whitespace-nowrap text-sm font-medium text-gray-700 w-0">
                      {marketCapRanking.get(coin.id)}
                    </td>
                    <td className="py-4 pl-7 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-white font-bold mr-3 shadow-md">
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

export default EthCoins;
