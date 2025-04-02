import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const BnbCoins = () => {
  // Filter BNB coins
  const bnbCoins = coins.filter((coin) => coin.categories.includes("bnb"));

  // Define colors for BNB theme
  const bnbColors = {
    gradient: "from-yellow-400 to-yellow-500",
    bg: "bg-yellow-50",
    text: "text-yellow-600",
    highlight: "text-yellow-500",
    hover: "hover:text-yellow-200",
    ring: "yellow",
    hoverBg: "yellow",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={bnbCoins}
        categoryId="bnb"
        title="BNB Crypto Market Overview"
        colors={bnbColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={bnbCoins}
        categoryId="bnb"
        title="Cryptocurrency Prices by Market Cap"
        colors={bnbColors}
      />
    </div>
  );
};

export default BnbCoins;
