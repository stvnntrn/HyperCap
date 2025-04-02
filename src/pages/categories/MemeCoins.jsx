import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const MemeCoins = () => {
  // Filter Meme coins
  const memeCoins = coins.filter((coin) => coin.categories.includes("meme"));

  // Define colors for Meme theme
  const memeColors = {
    gradient: "from-[#FF6B6B] to-[#FFD93D]",
    bg: "bg-[#FF6B6B]/10",
    text: "text-[#FF6B6B]",
    highlight: "text-[#FF6B6B]",
    hover: "hover:text-[#FF6B6B]",
    ring: "[#FF6B6B]",
    hoverBg: "[#FF6B6B]",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={memeCoins}
        categoryId="meme"
        title="Meme Crypto Market Overview"
        colors={memeColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={memeCoins}
        categoryId="meme"
        title="Cryptocurrency Prices by Market Cap"
        colors={memeColors}
      />
    </div>
  );
};

export default MemeCoins;
