import { coins } from "../../data/coins";
import CryptoTable from "../../components/CryptoTable";

const BnbCoins = () => {
  // Filter BNB coins
  const bnbCoins = coins.filter((coin) => coin.categories.includes("bnb"));

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

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <h2 className="text-2xl font-bold mb-6 flex items-center">
        BNB Chain Ecosystem
        <span className="bg-gradient-to-r from-yellow-500 to-yellow-700 text-white text-xs px-2 py-1 rounded-full ml-3">
          LIVE
        </span>
      </h2>

      <CryptoTable
        coins={bnbCoins}
        searchPlaceholder="Search BNB coins..."
        gradientColors="from-yellow-500 to-yellow-700"
        getTrendIndicator={getTrendIndicator}
      />
    </div>
  );
};

export default BnbCoins;
