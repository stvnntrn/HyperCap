import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const DefiCoins = () => {
  // Filter DeFi coins
  const defiCoins = coins.filter((coin) => coin.categories.includes("defi"));

  // Define colors for DeFi theme
  const defiColors = {
    gradient: "from-[#00B4DB] to-[#00F260]",
    bg: "bg-[#00B4DB]/10",
    text: "text-[#00B4DB]",
    highlight: "text-[#00B4DB]",
    hover: "hover:text-[#00B4DB]",
    ring: "[#00B4DB]",
    hoverBg: "[#00B4DB]",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={defiCoins}
        categoryId="defi"
        title="DeFi Crypto Market Overview"
        colors={defiColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={defiCoins}
        categoryId="defi"
        title="Cryptocurrency Prices by Market Cap"
        colors={defiColors}
      />
    </div>
  );
};

export default DefiCoins;
