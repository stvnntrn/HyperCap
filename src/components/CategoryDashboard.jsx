import {
  TrendingUp,
  TrendingDown,
  Activity,
  DollarSign,
  ArrowUpRight,
  PlusCircle,
  Rocket,
} from "lucide-react";
import { formatNumber, formatCompactNumber } from "../utils/formatNumber";

const CategoryDashboard = ({
  coins,
  categoryId,
  title,
  colors = {
    gradient: "from-teal-400 to-teal-500",
    bg: "bg-teal-50",
    text: "text-teal-600",
    highlight: "text-teal-500",
    hover: "hover:text-teal-200",
    ring: "teal",
    hoverBg: "teal",
  },
}) => {
  // Calculate total market cap and volume
  const totalMarketCap = coins.reduce((sum, coin) => sum + coin.marketCap, 0);
  const totalVolume = coins.reduce((sum, coin) => sum + coin.volume, 0);

  // Get trending coins by volume
  const trendingCoins = [...coins]
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 3);

  // Get top gainers
  const topGainers = [...coins]
    .sort((a, b) => b.change24h - a.change24h)
    .slice(0, 3);

  // Get newly listed coins (using market cap as a proxy for listing time)
  const newlyListed = [...coins]
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
      return formatCompactNumber(value);
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
          stroke={isPositive ? "#3b82f6" : "#ef4444"}
          strokeWidth="2"
          fill="none"
        />
        <path
          d={`${pathString} L ${width - padding.right} ${
            height - padding.bottom
          } L ${padding.left} ${height - padding.bottom} Z`}
          fill={
            isPositive ? "rgba(59, 130, 246, 0.1)" : "rgba(239, 68, 68, 0.1)"
          }
        />
      </svg>
    );
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 flex items-center">
        {title || `${categoryId.toUpperCase()} Crypto Market Overview`}
        <span
          className={`bg-gradient-to-r ${colors.gradient} text-white text-xs px-2 py-1 rounded-full ml-3`}
        >
          LIVE
        </span>
      </h2>

      <div className="grid grid-cols-12 gap-4">
        {/* Market Cap Chart */}
        <div className="col-span-6 rounded-xl shadow-[0_4px_12px_-2px_rgba(0,0,0,0.15)] hover:shadow-[0_6px_16px_-2px_rgba(0,0,0,0.2)] transition-all overflow-hidden bg-white">
          <div className="p-3 font-medium flex items-center justify-between">
            <div className={`flex items-center ${colors.text}`}>
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
              {formatCompactNumber(totalMarketCap)}
            </div>
            <div className="h-[120px]">
              {generateLineChart(marketCapChartData)}
            </div>
          </div>
        </div>

        {/* Volume Chart */}
        <div className="col-span-6 rounded-xl shadow-[0_4px_12px_-2px_rgba(0,0,0,0.15)] hover:shadow-[0_6px_16px_-2px_rgba(0,0,0,0.2)] transition-all overflow-hidden bg-white">
          <div className="p-3 font-medium flex items-center justify-between">
            <div className={`flex items-center ${colors.text}`}>
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
              {formatCompactNumber(totalVolume)}
            </div>
            <div className="h-[120px]">
              {generateLineChart(volumeChartData, false)}
            </div>
          </div>
        </div>

        {/* Trending Coins */}
        <div className="col-span-4 rounded-xl shadow-[0_4px_12px_-2px_rgba(0,0,0,0.15)] hover:shadow-[0_6px_16px_-2px_rgba(0,0,0,0.2)] transition-all overflow-hidden bg-white">
          <div
            className={`text-base ${colors.text} font-medium flex items-center gap-2 px-4 pt-4 pb-2`}
          >
            <TrendingUp size={16} />
            Trending
          </div>
          <div>
            {trendingCoins.map((coin, index) => (
              <div
                key={index}
                className={`flex items-center justify-between hover:${colors.bg} transition-colors group px-4 py-3 cursor-pointer`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className={`h-6 w-6 rounded-full bg-gradient-to-br ${colors.gradient} flex items-center justify-center text-white font-bold text-xs shadow-sm flex-shrink-0`}
                  >
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
                    ${formatNumber(coin.price)}
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
          <div
            className={`text-base ${colors.text} font-medium flex items-center gap-2 px-4 pt-4 pb-2`}
          >
            <Rocket size={16} />
            Top Gainers
          </div>
          <div>
            {topGainers.map((coin, index) => (
              <div
                key={index}
                className={`flex items-center justify-between hover:${colors.bg} transition-colors group px-4 py-3 cursor-pointer`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className={`h-6 w-6 rounded-full bg-gradient-to-br ${colors.gradient} flex items-center justify-center text-white font-bold text-xs shadow-sm flex-shrink-0`}
                  >
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
                    ${formatNumber(coin.price)}
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
          <div
            className={`text-base ${colors.text} font-medium flex items-center gap-2 px-4 pt-4 pb-2`}
          >
            <PlusCircle size={16} />
            Newly Listed
          </div>
          <div>
            {newlyListed.map((coin, index) => (
              <div
                key={index}
                className={`flex items-center justify-between hover:${colors.bg} transition-colors group px-4 py-3 cursor-pointer`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className={`h-6 w-6 rounded-full bg-gradient-to-br ${colors.gradient} flex items-center justify-center text-white font-bold text-xs shadow-sm flex-shrink-0`}
                  >
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
                    ${formatNumber(coin.price)}
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
    </div>
  );
};

export default CategoryDashboard;
