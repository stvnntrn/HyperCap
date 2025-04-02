import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const AiCoins = () => {
  // Filter AI coins
  const aiCoins = coins.filter((coin) => coin.categories.includes("ai"));

  // Define colors for AI theme
  const aiColors = {
    gradient: "from-[#101820] to-[#00A6FF]",
    bg: "bg-[#101820]/10",
    text: "text-[#00A6FF]",
    highlight: "text-[#00A6FF]",
    hover: "hover:text-[#00A6FF]",
    ring: "[#00A6FF]",
    hoverBg: "[#00A6FF]",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={aiCoins}
        categoryId="ai"
        title="AI Crypto Market Overview"
        colors={aiColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={aiCoins}
        categoryId="ai"
        title="Cryptocurrency Prices by Market Cap"
        colors={aiColors}
      />
    </div>
  );
};

export default AiCoins;
