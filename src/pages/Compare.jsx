import { useState, useEffect, useRef } from "react";
import { coins } from "../data/coins";
import { Search, ArrowDown, X, TrendingUp, ArrowLeftRight } from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LabelList,
} from "recharts";

const Compare = () => {
  const [coin1, setCoin1] = useState("");
  const [coin2, setCoin2] = useState("");
  const [searchQuery1, setSearchQuery1] = useState("");
  const [searchQuery2, setSearchQuery2] = useState("");
  const [showDropdown1, setShowDropdown1] = useState(false);
  const [showDropdown2, setShowDropdown2] = useState(false);
  const dropdownRef1 = useRef(null);
  const dropdownRef2 = useRef(null);
  const [timeRange1, setTimeRange1] = useState("24h");
  const [timeRange2, setTimeRange2] = useState("24h");

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef1.current &&
        !dropdownRef1.current.contains(event.target)
      ) {
        setShowDropdown1(false);
      }
      if (
        dropdownRef2.current &&
        !dropdownRef2.current.contains(event.target)
      ) {
        setShowDropdown2(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Filter coins based on search query
  const filteredCoins1 = coins.filter(
    (coin) =>
      coin.name.toLowerCase().includes(searchQuery1.toLowerCase()) ||
      coin.symbol.toLowerCase().includes(searchQuery1.toLowerCase())
  );

  const filteredCoins2 = coins.filter(
    (coin) =>
      coin.name.toLowerCase().includes(searchQuery2.toLowerCase()) ||
      coin.symbol.toLowerCase().includes(searchQuery2.toLowerCase())
  );

  // Get selected coin data
  const selectedCoin1 = coins.find((coin) => coin.id === coin1);
  const selectedCoin2 = coins.find((coin) => coin.id === coin2);

  // Generate sample chart data based on time range
  const getChartData = (coin, timeRange) => {
    if (!coin) return [];
    const currentPrice = coin.price || 0;
    let data = [];
    const now = new Date();

    switch (timeRange) {
      case "24h":
        // Generate 6 points for the last 24 hours
        data = [
          {
            name: new Date(now - 24 * 60 * 60 * 1000).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
            value: currentPrice * 0.95,
          },
          {
            name: new Date(now - 19.2 * 60 * 60 * 1000).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
            value: currentPrice * 0.98,
          },
          {
            name: new Date(now - 14.4 * 60 * 60 * 1000).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
            value: currentPrice * 1.02,
          },
          {
            name: new Date(now - 9.6 * 60 * 60 * 1000).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
            value: currentPrice * 1.05,
          },
          {
            name: new Date(now - 4.8 * 60 * 60 * 1000).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
            value: currentPrice * 1.01,
          },
          {
            name: now.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
            value: currentPrice,
          },
        ];
        break;
      case "7d":
        // Generate 7 points for the last 7 days
        data = [
          {
            name: new Date(now - 7 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 0.98,
          },
          {
            name: new Date(now - 5.8 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 0.95,
          },
          {
            name: new Date(now - 4.6 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 1.02,
          },
          {
            name: new Date(now - 3.4 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 0.97,
          },
          {
            name: new Date(now - 2.2 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 1.03,
          },
          {
            name: new Date(now - 1 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 0.99,
          },
          {
            name: now.toLocaleDateString([], {
              month: "short",
              day: "numeric",
            }),
            value: currentPrice,
          },
        ];
        break;
      case "30d":
        // Generate 6 points for the last 30 days
        data = [
          {
            name: new Date(now - 30 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 0.95,
          },
          {
            name: new Date(now - 24 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 1.02,
          },
          {
            name: new Date(now - 18 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 0.98,
          },
          {
            name: new Date(now - 12 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 1.05,
          },
          {
            name: new Date(now - 6 * 24 * 60 * 60 * 1000).toLocaleDateString(
              [],
              {
                month: "short",
                day: "numeric",
              }
            ),
            value: currentPrice * 1.01,
          },
          {
            name: now.toLocaleDateString([], {
              month: "short",
              day: "numeric",
            }),
            value: currentPrice,
          },
        ];
        break;
      case "all":
        // Generate 6 points for the last year
        data = [
          {
            name: new Date(
              now - 12 * 30 * 24 * 60 * 60 * 1000
            ).toLocaleDateString([], {
              month: "short",
              year: "numeric",
            }),
            value: currentPrice * 0.95,
          },
          {
            name: new Date(
              now - 8 * 30 * 24 * 60 * 60 * 1000
            ).toLocaleDateString([], {
              month: "short",
              year: "numeric",
            }),
            value: currentPrice * 1.02,
          },
          {
            name: new Date(
              now - 6 * 30 * 24 * 60 * 60 * 1000
            ).toLocaleDateString([], {
              month: "short",
              year: "numeric",
            }),
            value: currentPrice * 0.98,
          },
          {
            name: new Date(
              now - 4 * 30 * 24 * 60 * 60 * 1000
            ).toLocaleDateString([], {
              month: "short",
              year: "numeric",
            }),
            value: currentPrice * 1.05,
          },
          {
            name: new Date(
              now - 2 * 30 * 24 * 60 * 60 * 1000
            ).toLocaleDateString([], {
              month: "short",
              year: "numeric",
            }),
            value: currentPrice * 1.01,
          },
          {
            name: now.toLocaleDateString([], {
              month: "short",
              year: "numeric",
            }),
            value: currentPrice,
          },
        ];
        break;
    }
    return data;
  };

  // Format number with appropriate suffix
  const formatNumber = (num) => {
    if (!num) return "0";
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) {
      const kValue = num / 1e3;
      return `$${kValue % 1 === 0 ? kValue.toFixed(0) : kValue.toFixed(2)}K`;
    }
    return `$${num.toFixed(2)}`;
  };

  const formatPrice = (price) => {
    if (!price) return "$0.00";
    if (price >= 1e12) return `$${(price / 1e12).toFixed(2)}T`;
    if (price >= 1e9) return `$${(price / 1e9).toFixed(2)}B`;
    if (price >= 1e6) return `$${(price / 1e6).toFixed(2)}M`;
    if (price >= 1e3) {
      const kValue = price / 1e3;
      return `$${kValue % 1 === 0 ? kValue.toFixed(0) : kValue.toFixed(2)}K`;
    }
    return `$${price.toFixed(2)}`;
  };

  const formatPercentage = (change) => {
    if (!change) return "0.00%";
    return `${change.toFixed(2)}%`;
  };

  const formatSupply = (supply) => {
    if (!supply) return "0";
    if (supply >= 1e12) return `${(supply / 1e12).toFixed(2)}T`;
    if (supply >= 1e9) return `${(supply / 1e9).toFixed(2)}B`;
    if (supply >= 1e6) return `${(supply / 1e6).toFixed(2)}M`;
    if (supply >= 1e3) {
      const kValue = supply / 1e3;
      return `${kValue % 1 === 0 ? kValue.toFixed(0) : kValue.toFixed(2)}K`;
    }
    return supply.toString();
  };

  const switchCoins = () => {
    // Switch coin1 and coin2
    const temp = coin1;
    setCoin1(coin2);
    setCoin2(temp);

    // Switch search queries
    const tempQuery = searchQuery1;
    setSearchQuery1(searchQuery2);
    setSearchQuery2(tempQuery);
  };

  // Calculate Y-axis domain
  const calculateYAxisDomain = (data) => {
    if (!data || data.length === 0) return [0, 0];

    const values = data.map((d) => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);

    // Calculate 10% padding for better visualization
    const padding = (max - min) * 0.1;
    const domainMin = Math.max(0, min - padding);
    const domainMax = max + padding;

    // Round the values to make the chart look cleaner
    const roundToSignificantFigures = (num, sigFigs) => {
      if (num === 0) return 0;
      const d = Math.ceil(Math.log10(Math.abs(num)));
      const power = sigFigs - d;
      const magnitude = Math.pow(10, power);
      const shifted = Math.round(num * magnitude);
      return shifted / magnitude;
    };

    return [
      roundToSignificantFigures(domainMin, 2),
      roundToSignificantFigures(domainMax, 2),
    ];
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl max-w-7xl">
      <h1 className="text-3xl font-bold mb-8 text-center">
        Cryptocurrency Comparison Tool
      </h1>

      <div className="grid grid-cols-2 gap-8 max-w-6xl mx-auto">
        {/* First Coin Selector */}
        <div className="relative" ref={dropdownRef1}>
          <div className="relative">
            <div
              onClick={() => {
                if (!showDropdown1 && !searchQuery1) {
                  setCoin1("");
                }
                setShowDropdown1(!showDropdown1);
              }}
              className="w-full p-4 border border-gray-300 rounded-lg cursor-pointer flex items-center justify-between hover:border-teal-500 transition-colors"
            >
              {showDropdown1 ? (
                <div className="relative w-full">
                  <Search
                    size={16}
                    className="absolute left-0 top-1/2 transform -translate-y-1/2 text-teal-500"
                  />
                  <input
                    type="text"
                    placeholder="Select First Coin"
                    value={searchQuery1}
                    onChange={(e) => {
                      setSearchQuery1(e.target.value);
                      if (!e.target.value) {
                        setCoin1("");
                      }
                    }}
                    onClick={(e) => e.stopPropagation()}
                    onDoubleClick={(e) => e.stopPropagation()}
                    className="w-full pl-6 pr-4 focus:outline-none"
                    autoFocus
                  />
                </div>
              ) : selectedCoin1 ? (
                <div className="flex items-center gap-2 w-full">
                  <div className="h-6 w-6 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center text-white font-bold text-xs">
                    {selectedCoin1.symbol.charAt(0)}
                  </div>
                  <span className="flex-grow">{selectedCoin1.name}</span>
                </div>
              ) : (
                <span className="text-gray-700">Select First Coin</span>
              )}
              {selectedCoin1 ? (
                <X
                  size={16}
                  className="hover:text-teal-600 cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    setCoin1("");
                    setSearchQuery1("");
                  }}
                />
              ) : (
                <ArrowDown size={16} />
              )}
            </div>
            {showDropdown1 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto">
                <div className="py-1">
                  {filteredCoins1.map((coin) => (
                    <div
                      key={coin.id}
                      onClick={() => {
                        setCoin1(coin.id);
                        setShowDropdown1(false);
                      }}
                      className="flex items-center gap-2 px-4 py-2 hover:bg-teal-50 cursor-pointer"
                    >
                      <div className="h-6 w-6 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center text-white font-bold text-xs">
                        {coin.symbol.charAt(0)}
                      </div>
                      <div>
                        <div className="font-medium">{coin.name}</div>
                        <div className="text-sm text-gray-500">
                          {coin.symbol}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Second Coin Selector */}
        <div className="relative" ref={dropdownRef2}>
          <div className="relative">
            <div
              onClick={() => {
                if (!showDropdown2 && !searchQuery2) {
                  setCoin2("");
                }
                setShowDropdown2(!showDropdown2);
              }}
              className="w-full p-4 border border-gray-300 rounded-lg cursor-pointer flex items-center justify-between hover:border-teal-500 transition-colors"
            >
              {showDropdown2 ? (
                <div className="relative w-full">
                  <Search
                    size={16}
                    className="absolute left-0 top-1/2 transform -translate-y-1/2 text-teal-500"
                  />
                  <input
                    type="text"
                    placeholder="Select Second Coin"
                    value={searchQuery2}
                    onChange={(e) => {
                      setSearchQuery2(e.target.value);
                      if (!e.target.value) {
                        setCoin2("");
                      }
                    }}
                    onClick={(e) => e.stopPropagation()}
                    onDoubleClick={(e) => e.stopPropagation()}
                    className="w-full pl-6 pr-4 focus:outline-none"
                    autoFocus
                  />
                </div>
              ) : selectedCoin2 ? (
                <div className="flex items-center gap-2 w-full">
                  <div className="h-6 w-6 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center text-white font-bold text-xs">
                    {selectedCoin2.symbol.charAt(0)}
                  </div>
                  <span className="flex-grow">{selectedCoin2.name}</span>
                </div>
              ) : (
                <span className="text-gray-700">Select Second Coin</span>
              )}
              {selectedCoin2 ? (
                <X
                  size={16}
                  className="hover:text-teal-600 cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    setCoin2("");
                    setSearchQuery2("");
                  }}
                />
              ) : (
                <ArrowDown size={16} />
              )}
            </div>
            {showDropdown2 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto">
                <div className="py-1">
                  {filteredCoins2.map((coin) => (
                    <div
                      key={coin.id}
                      onClick={() => {
                        setCoin2(coin.id);
                        setShowDropdown2(false);
                      }}
                      className="flex items-center gap-2 px-4 py-2 hover:bg-teal-50 cursor-pointer"
                    >
                      <div className="h-6 w-6 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center text-white font-bold text-xs">
                        {coin.symbol.charAt(0)}
                      </div>
                      <div>
                        <div className="font-medium">{coin.name}</div>
                        <div className="text-sm text-gray-500">
                          {coin.symbol}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Coin Cards */}
      <div className="relative grid grid-cols-2 gap-8 max-w-6xl mx-auto mt-8">
        {/* First Coin Card */}
        <div className="bg-white rounded-2xl px-6 pt-6 pb-4 border border-gray-200 shadow-lg">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-teal-500 to-teal-600 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-white">
                  {selectedCoin1 ? selectedCoin1.symbol.charAt(0) : "?"}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedCoin1 ? selectedCoin1.name : "Select First Coin"}
                </h2>
                <p className="text-gray-500">
                  {selectedCoin1
                    ? selectedCoin1.symbol
                    : "Choose a coin to compare"}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-gray-900">
                {selectedCoin1 ? formatPrice(selectedCoin1.price) : "$0.00"}
              </p>
              <p
                className={`text-sm ${
                  (selectedCoin1?.change24h || 0) >= 0
                    ? "text-green-500"
                    : "text-red-500"
                }`}
              >
                {selectedCoin1
                  ? formatPercentage(selectedCoin1.change24h)
                  : "0.00%"}
                <TrendingUp className="inline ml-1" size={16} />
              </p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6 pl-4">
            <div>
              <div className="text-sm text-gray-500">Market Cap</div>
              <div className="text-lg font-semibold">
                {formatNumber(selectedCoin1?.marketCap)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">24h Volume</div>
              <div className="text-lg font-semibold">
                {formatNumber(selectedCoin1?.volume)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Circulating Supply</div>
              <div className="text-lg font-semibold">
                {formatSupply(selectedCoin1?.circulatingSupply)}
              </div>
            </div>
          </div>

          <div className="h-48 relative mt-6">
            {selectedCoin1 ? (
              <>
                <div className="absolute -top-3 right-5 z-10 flex space-x-1 bg-white rounded-lg shadow-sm p-1">
                  {["24h", "7d", "30d", "all"].map((range) => (
                    <button
                      key={range}
                      onClick={() => setTimeRange1(range)}
                      className={`px-2 py-1 text-xs rounded ${
                        timeRange1 === range
                          ? "bg-teal-500 text-white"
                          : "text-gray-600 hover:bg-gray-100"
                      }`}
                    >
                      {range}
                    </button>
                  ))}
                </div>
                <div className="w-full h-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={getChartData(selectedCoin1, timeRange1)}
                      margin={{ top: 30, right: 20, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis
                        dataKey="name"
                        stroke="#6b7280"
                        tick={{ fontSize: 12 }}
                      />
                      <YAxis
                        stroke="#6b7280"
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => formatPrice(value)}
                        domain={calculateYAxisDomain(
                          getChartData(selectedCoin1, timeRange1)
                        )}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "white",
                          border: "1px solid #e5e7eb",
                          borderRadius: "0.5rem",
                          color: "#1f2937",
                        }}
                        formatter={(value) => [formatPrice(value), "Price"]}
                      />
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#14b8a6"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                Select a coin to view chart
              </div>
            )}
          </div>
        </div>

        {/* Switch Button */}
        <button
          onClick={switchCoins}
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 
                     bg-teal-500 rounded-full p-3 z-10 hover:bg-teal-600 transition-colors
                     shadow-lg hover:shadow-xl"
        >
          <ArrowLeftRight className="text-white" size={24} />
        </button>

        {/* Second Coin Card */}
        <div className="bg-white rounded-2xl px-6 pt-6 pb-4 border border-gray-200 shadow-lg">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-teal-500 to-teal-600 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-white">
                  {selectedCoin2 ? selectedCoin2.symbol.charAt(0) : "?"}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedCoin2 ? selectedCoin2.name : "Select Second Coin"}
                </h2>
                <p className="text-gray-500">
                  {selectedCoin2
                    ? selectedCoin2.symbol
                    : "Choose a coin to compare"}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-gray-900">
                {selectedCoin2 ? formatPrice(selectedCoin2.price) : "$0.00"}
              </p>
              <p
                className={`text-sm ${
                  (selectedCoin2?.change24h || 0) >= 0
                    ? "text-green-500"
                    : "text-red-500"
                }`}
              >
                {selectedCoin2
                  ? formatPercentage(selectedCoin2.change24h)
                  : "0.00%"}
                <TrendingUp className="inline ml-1" size={16} />
              </p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6 pl-4">
            <div>
              <div className="text-sm text-gray-500">Market Cap</div>
              <div className="text-lg font-semibold">
                {formatNumber(selectedCoin2?.marketCap)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">24h Volume</div>
              <div className="text-lg font-semibold">
                {formatNumber(selectedCoin2?.volume)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Circulating Supply</div>
              <div className="text-lg font-semibold">
                {formatSupply(selectedCoin2?.circulatingSupply)}
              </div>
            </div>
          </div>

          <div className="h-48 relative mt-6">
            {selectedCoin2 ? (
              <>
                <div className="absolute -top-3 right-5 z-10 flex space-x-1 bg-white rounded-lg shadow-sm p-1">
                  {["24h", "7d", "30d", "all"].map((range) => (
                    <button
                      key={range}
                      onClick={() => setTimeRange2(range)}
                      className={`px-2 py-1 text-xs rounded ${
                        timeRange2 === range
                          ? "bg-teal-500 text-white"
                          : "text-gray-600 hover:bg-gray-100"
                      }`}
                    >
                      {range}
                    </button>
                  ))}
                </div>
                <div className="w-full h-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={getChartData(selectedCoin2, timeRange2)}
                      margin={{ top: 30, right: 20, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis
                        dataKey="name"
                        stroke="#6b7280"
                        tick={{ fontSize: 12 }}
                      />
                      <YAxis
                        stroke="#6b7280"
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => formatPrice(value)}
                        domain={calculateYAxisDomain(
                          getChartData(selectedCoin2, timeRange2)
                        )}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "white",
                          border: "1px solid #e5e7eb",
                          borderRadius: "0.5rem",
                          color: "#1f2937",
                        }}
                        formatter={(value) => [formatPrice(value), "Price"]}
                      />
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#14b8a6"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                Select a coin to view chart
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Market Cap Comparison Section */}
      {selectedCoin1 && selectedCoin2 && (
        <div className="mt-8">
          <h2 className="text-xl font-bold text-gray-900 text-center mb-6">
            If {selectedCoin1.name} reaches {selectedCoin2.name}&apos;s market
            cap
          </h2>
          <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
            {/* Market Cap Multiplier Card */}
            <div className="bg-white rounded-2xl p-4 border border-gray-200 shadow-lg">
              <h3 className="text-sm font-semibold text-gray-900 text-center mb-2">
                Market Cap Multiplier
              </h3>
              <div
                className={`text-2xl font-bold text-center ${
                  selectedCoin2.marketCap > selectedCoin1.marketCap
                    ? "text-green-500"
                    : "text-red-500"
                }`}
              >
                {(selectedCoin2.marketCap / selectedCoin1.marketCap).toFixed(2)}
                x
              </div>
            </div>

            {/* Potential Price Card */}
            <div className="bg-white rounded-2xl p-4 border border-gray-200 shadow-lg">
              <h3 className="text-sm font-semibold text-gray-900 text-center mb-2">
                {selectedCoin1.name} Price
              </h3>
              <div
                className={`text-2xl font-bold text-center ${
                  selectedCoin2.marketCap > selectedCoin1.marketCap
                    ? "text-green-500"
                    : "text-red-500"
                }`}
              >
                {formatPrice(
                  selectedCoin1.price *
                    (selectedCoin2.marketCap / selectedCoin1.marketCap)
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Comparative Charts */}
      {selectedCoin1 && selectedCoin2 && (
        <div className="mt-8">
          <h2 className="text-xl font-bold text-gray-900 text-center mb-4">
            Comparison Charts
          </h2>
          <div className="flex justify-center items-center gap-4 mb-6">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-teal-500"></div>
              <span className="text-sm text-gray-600">
                {selectedCoin1.name}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-blue-500"></div>
              <span className="text-sm text-gray-600">
                {selectedCoin2.name}
              </span>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 max-w-6xl mx-auto">
            {/* Market Cap Pie Chart */}
            <div className="bg-white rounded-2xl p-4 border border-gray-200 shadow-lg">
              <h3 className="text-sm font-semibold text-gray-900 text-center mb-2">
                Market Cap
              </h3>
              <ResponsiveContainer width="100%" height={120}>
                <PieChart>
                  <Pie
                    data={[
                      {
                        name: selectedCoin1.name,
                        value: selectedCoin1.marketCap,
                        color: "#14b8a6",
                      },
                      {
                        name: selectedCoin2.name,
                        value: selectedCoin2.marketCap,
                        color: "#3b82f6",
                      },
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={50}
                    dataKey="value"
                    label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                    activeShape={{
                      stroke: "none",
                      strokeWidth: 0,
                    }}
                  >
                    <Cell fill="#14b8a6" />
                    <Cell fill="#3b82f6" />
                  </Pie>
                  <Tooltip
                    content={({ payload }) => (
                      <div className="bg-white p-2 rounded shadow border border-gray-200">
                        <div className="font-semibold text-gray-700">
                          Marketcap
                        </div>
                        {payload.map((entry, index) => (
                          <div
                            key={`item-${index}`}
                            style={{
                              color: index === 0 ? "#14b8a6" : "#3b82f6",
                            }}
                          >
                            {entry.name}: {formatNumber(entry.value)}
                          </div>
                        ))}
                      </div>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Volume Bar Chart */}
            <div className="bg-white rounded-2xl p-4 border border-gray-200 shadow-lg">
              <h3 className="text-sm font-semibold text-gray-900 text-center mb-2">
                Volume
              </h3>
              <ResponsiveContainer width="100%" height={120}>
                <BarChart
                  data={[
                    {
                      name: selectedCoin1.name,
                      value: selectedCoin1.volume,
                      fill: "#14b8a6",
                    },
                    {
                      name: selectedCoin2.name,
                      value: selectedCoin2.volume,
                      fill: "#3b82f6",
                    },
                  ]}
                  layout="vertical"
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#e5e7eb"
                    horizontal={false}
                  />
                  <XAxis type="number" hide />
                  <YAxis type="category" dataKey="name" hide />
                  <Tooltip
                    trigger="hover"
                    shared={false}
                    cursor={{ fill: "transparent" }}
                    content={({ payload }) => (
                      <div className="bg-white p-2 rounded shadow border border-gray-200">
                        <div className="font-semibold text-gray-700">
                          Volume
                        </div>
                        {payload?.map((entry, index) => (
                          <div
                            key={`item-${index}`}
                            style={{ color: entry.payload.fill }}
                          >
                            {entry.payload.name}: {formatNumber(entry.value)}
                          </div>
                        ))}
                      </div>
                    )}
                  />
                  <Bar
                    dataKey="value"
                    fill="#14b8a6"
                    radius={[0, 4, 4, 0]}
                    barSize={30}
                    barGap={20}
                  >
                    <LabelList
                      dataKey="value"
                      position="top"
                      formatter={(value) => formatNumber(value)}
                      style={{
                        fontSize: "12px",
                        fill: "#1f2937",
                        fontWeight: "bold",
                      }}
                    />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Supply Bar Chart */}
            <div className="bg-white rounded-2xl p-4 border border-gray-200 shadow-lg">
              <h3 className="text-sm font-semibold text-gray-900 text-center mb-2">
                Circulating Supply
              </h3>
              <div className="pr-8">
                <ResponsiveContainer width="100%" height={120}>
                  <BarChart
                    data={[
                      {
                        name: "Supply",
                        [selectedCoin1.name]: selectedCoin1.circulatingSupply,
                        [selectedCoin2.name]: selectedCoin2.circulatingSupply,
                      },
                    ]}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="name" stroke="#6b7280" hide />
                    <YAxis
                      stroke="#6b7280"
                      tickFormatter={(value) => formatSupply(value)}
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip
                      trigger="hover"
                      shared={false}
                      contentStyle={{
                        backgroundColor: "white",
                        border: "1px solid #e5e7eb",
                        borderRadius: "0.5rem",
                        color: "#1f2937",
                      }}
                      formatter={(value, name) => [formatSupply(value), name]}
                      labelStyle={{ color: "#1f2937", fontWeight: "600" }}
                      cursor={{ fill: "transparent" }}
                    />
                    <Bar
                      dataKey={selectedCoin1.name}
                      fill="#14b8a6"
                      barSize={30}
                    />
                    <Bar
                      dataKey={selectedCoin2.name}
                      fill="#3b82f6"
                      barSize={30}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Compare;
