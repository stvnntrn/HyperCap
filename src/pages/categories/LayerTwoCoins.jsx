import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const LayerTwoCoins = () => {
  // Filter Layer 2 coins
  const layerTwoCoins = coins.filter((coin) =>
    coin.categories.includes("layer2")
  );

  // Define colors for Layer 2 theme
  const layerTwoColors = {
    gradient: "from-[#4ECDC4] to-[#45B7D1]",
    bg: "bg-[#4ECDC4]/10",
    text: "text-[#4ECDC4]",
    highlight: "text-[#4ECDC4]",
    hover: "hover:text-[#4ECDC4]",
    ring: "[#4ECDC4]",
    hoverBg: "[#4ECDC4]",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={layerTwoCoins}
        categoryId="layer2"
        title="Layer 2 Crypto Market Overview"
        colors={layerTwoColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={layerTwoCoins}
        categoryId="layer2"
        title="Cryptocurrency Prices by Market Cap"
        colors={layerTwoColors}
      />
    </div>
  );
};

export default LayerTwoCoins;
