import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const RwaCoins = () => {
  // Filter RWA coins
  const rwaCoins = coins.filter((coin) => coin.categories.includes("rwa"));

  // Define colors for RWA theme
  const rwaColors = {
    gradient: "from-[#00FA9A] to-[#008C5E]",
    bg: "bg-[#00FA9A]/10",
    text: "text-[#00FA9A]",
    highlight: "text-[#00FA9A]",
    hover: "hover:text-[#00FA9A]",
    ring: "[#00FA9A]",
    hoverBg: "[#00FA9A]",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={rwaCoins}
        categoryId="rwa"
        title="RWA Crypto Market Overview"
        colors={rwaColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={rwaCoins}
        categoryId="rwa"
        title="Cryptocurrency Prices by Market Cap"
        colors={rwaColors}
      />
    </div>
  );
};

export default RwaCoins;
