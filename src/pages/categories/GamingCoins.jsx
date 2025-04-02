import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const GamingCoins = () => {
  // Filter Gaming coins
  const gamingCoins = coins.filter((coin) =>
    coin.categories.includes("gaming")
  );

  // Define colors for Gaming theme
  const gamingColors = {
    gradient: "from-[#FF9A4B] to-[#5D3FD3]",
    bg: "bg-[#FF9A4B]/10",
    text: "text-[#FF9A4B]",
    highlight: "text-[#FF9A4B]",
    hover: "hover:text-[#FF9A4B]",
    ring: "[#FF9A4B]",
    hoverBg: "[#FF9A4B]",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={gamingCoins}
        categoryId="gaming"
        title="Gaming Crypto Market Overview"
        colors={gamingColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={gamingCoins}
        categoryId="gaming"
        title="Cryptocurrency Prices by Market Cap"
        colors={gamingColors}
      />
    </div>
  );
};

export default GamingCoins;
