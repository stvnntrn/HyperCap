import { useState, useEffect, useRef } from "react";
import { coins } from "../data/coins";
import { Search, ArrowDown, X, TrendingUp } from "lucide-react";

const Compare = () => {
  const [coin1, setCoin1] = useState("");
  const [coin2, setCoin2] = useState("");
  const [searchQuery1, setSearchQuery1] = useState("");
  const [searchQuery2, setSearchQuery2] = useState("");
  const [showDropdown1, setShowDropdown1] = useState(false);
  const [showDropdown2, setShowDropdown2] = useState(false);
  const dropdownRef1 = useRef(null);
  const dropdownRef2 = useRef(null);

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

  // Generate sample chart data
  const getChartData = (coin) => {
    if (!coin) return [];
    // Generate a simpler set of data points with fixed values
    const basePrice = coin.price || 0;
    return [
      { value: basePrice * 0.95 },
      { value: basePrice * 1.02 },
      { value: basePrice * 0.98 },
      { value: basePrice * 1.05 },
      { value: basePrice * 1.01 },
      { value: basePrice },
    ];
  };

  // Generate line chart
  const generateLineChart = (data) => {
    if (!data || data.length === 0) return null;

    const width = 1000;
    const height = 120;
    const padding = { top: 20, right: 20, bottom: 30, left: 80 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const values = data.map((d) => d.value || 0);
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);

    // Format large numbers for y-axis
    const formatYAxisValue = (value) => {
      if (!value) return "$0";
      if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
      if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
      if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
      return `$${value.toFixed(0)}`;
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

        {/* Line */}
        <path d={pathString} stroke="#14b8a6" strokeWidth="2" fill="none" />
      </svg>
    );
  };

  // Format number with appropriate suffix
  const formatNumber = (num) => {
    if (!num) return "0";
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) return `$${(num / 1e3).toFixed(2)}K`;
    return `$${num.toFixed(2)}`;
  };

  const formatPrice = (price) => {
    if (!price) return "$0.00";
    return `$${price.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatPercentage = (change) => {
    if (!change) return "0.00%";
    return `${change.toFixed(2)}%`;
  };

  const formatSupply = (supply) => {
    if (!supply) return "0";
    if (supply >= 1e9) return `${(supply / 1e9).toFixed(2)}B`;
    if (supply >= 1e6) return `${(supply / 1e6).toFixed(2)}M`;
    if (supply >= 1e3) return `${(supply / 1e3).toFixed(2)}K`;
    return supply.toString();
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
      <div className="grid grid-cols-2 gap-8 max-w-6xl mx-auto mt-8">
        {/* First Coin Card */}
        <div className="bg-white rounded-2xl p-6 space-y-6 border border-gray-200 shadow-lg">
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

          <div className="grid grid-cols-3 gap-4 mt-6">
            <div>
              <div className="text-sm text-gray-500">Market Cap</div>
              <div className="text-lg font-semibold">
                {formatNumber(selectedCoin1?.marketCap)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">24h Volume</div>
              <div className="text-lg font-semibold">
                {formatNumber(selectedCoin1?.volume24h)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Circulating Supply</div>
              <div className="text-lg font-semibold">
                {formatSupply(selectedCoin1?.circulatingSupply)}
              </div>
            </div>
          </div>

          <div className="h-48">
            {selectedCoin1 ? (
              generateLineChart(getChartData(selectedCoin1))
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                Select a coin to view chart
              </div>
            )}
          </div>
        </div>

        {/* Second Coin Card */}
        <div className="bg-white rounded-2xl p-6 space-y-6 border border-gray-200 shadow-lg">
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

          <div className="grid grid-cols-3 gap-4 mt-6">
            <div>
              <div className="text-sm text-gray-500">Market Cap</div>
              <div className="text-lg font-semibold">
                {formatNumber(selectedCoin2?.marketCap)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">24h Volume</div>
              <div className="text-lg font-semibold">
                {formatNumber(selectedCoin2?.volume24h)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Circulating Supply</div>
              <div className="text-lg font-semibold">
                {formatSupply(selectedCoin2?.circulatingSupply)}
              </div>
            </div>
          </div>

          <div className="h-48">
            {selectedCoin2 ? (
              generateLineChart(getChartData(selectedCoin2))
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                Select a coin to view chart
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Compare;
