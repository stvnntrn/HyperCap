import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const InfrastructureCoins = () => {
  // Filter Infrastructure coins
  const infrastructureCoins = coins.filter((coin) =>
    coin.categories.includes("infrastructure")
  );

  // Define colors for Infrastructure theme
  const infrastructureColors = {
    gradient: "from-[#1A1A3A] to-[#4A4AFF]",
    bg: "bg-[#1A1A3A]/10",
    text: "text-[#1A1A3A]",
    highlight: "text-[#1A1A3A]",
    hover: "hover:text-[#1A1A3A]",
    ring: "[#1A1A3A]",
    hoverBg: "[#1A1A3A]",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={infrastructureCoins}
        categoryId="infrastructure"
        title="Infrastructure Crypto Market Overview"
        colors={infrastructureColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={infrastructureCoins}
        categoryId="infrastructure"
        title="Cryptocurrency Prices by Market Cap"
        colors={infrastructureColors}
      />
    </div>
  );
};

export default InfrastructureCoins;
