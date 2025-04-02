import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const LayerOneCoins = () => {
  // Filter Layer 1 coins
  const layerOneCoins = coins.filter((coin) =>
    coin.categories.includes("layer-1")
  );

  // Define colors for Layer 1 theme
  const layerOneColors = {
    gradient: "from-[#2962FF] to-[#0D47A1]",
    bg: "bg-[#2962FF]/10",
    text: "text-[#2962FF]",
    highlight: "text-[#2962FF]",
    hover: "hover:text-[#2962FF]",
    ring: "[#2962FF]",
    hoverBg: "[#2962FF]",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={layerOneCoins}
        categoryId="layer-1"
        title="Layer 1 Crypto Market Overview"
        colors={layerOneColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={layerOneCoins}
        categoryId="layer-1"
        title="Cryptocurrency Prices by Market Cap"
        colors={layerOneColors}
      />
    </div>
  );
};

export default LayerOneCoins;
