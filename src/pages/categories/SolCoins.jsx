import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const SolCoins = () => {
  // Filter SOL coins
  const solCoins = coins.filter((coin) => coin.categories.includes("sol"));

  // Define colors for SOL theme
  const solColors = {
    gradient: "from-[#7B4FFF] to-[#00D9B4]",
    bg: "bg-[#7B4FFF]/10",
    text: "text-[#7B4FFF]",
    highlight: "text-[#7B4FFF]",
    hover: "hover:text-[#7B4FFF]",
    ring: "[#7B4FFF]",
    hoverBg: "[#7B4FFF]",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={solCoins}
        categoryId="sol"
        title="SOL Crypto Market Overview"
        colors={solColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={solCoins}
        categoryId="sol"
        title="Cryptocurrency Prices by Market Cap"
        colors={solColors}
      />
    </div>
  );
};

export default SolCoins;
