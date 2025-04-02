import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const EthCoins = () => {
  // Filter ETH coins
  const ethCoins = coins.filter((coin) => coin.categories.includes("eth"));

  // Define colors for ETH theme
  const ethColors = {
    gradient: "from-gray-400 to-gray-500",
    bg: "bg-gray-50",
    text: "text-gray-600",
    highlight: "text-gray-500",
    hover: "hover:text-gray-200",
    ring: "gray",
    hoverBg: "gray",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={ethCoins}
        categoryId="eth"
        title="ETH Crypto Market Overview"
        colors={ethColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={ethCoins}
        categoryId="eth"
        title="Cryptocurrency Prices by Market Cap"
        colors={ethColors}
      />
    </div>
  );
};

export default EthCoins;
