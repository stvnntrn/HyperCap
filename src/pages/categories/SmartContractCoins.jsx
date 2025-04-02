import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const SmartContractCoins = () => {
  // Filter smart contract coins
  const smartContractCoins = coins.filter((coin) =>
    coin.categories.includes("smart-contracts")
  );

  // Define colors for Smart Contract theme
  const smartContractColors = {
    gradient: "from-indigo-400 to-purple-500",
    bg: "bg-indigo-50",
    text: "text-indigo-600",
    highlight: "text-indigo-500",
    hover: "hover:text-indigo-200",
    ring: "indigo",
    hoverBg: "indigo",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={smartContractCoins}
        categoryId="smart-contracts"
        title="Smart Contract Crypto Market Overview"
        colors={smartContractColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={smartContractCoins}
        categoryId="smart-contract"
        title="Cryptocurrency Prices by Market Cap"
        colors={smartContractColors}
      />
    </div>
  );
};

export default SmartContractCoins;
