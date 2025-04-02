import { coins } from "../../data/coins";
import CoinListTable from "../../components/CoinListTable";
import CategoryDashboard from "../../components/CategoryDashboard";

const NftCoins = () => {
  // Filter NFT coins
  const nftCoins = coins.filter((coin) => coin.categories.includes("nft"));

  // Define colors for NFT theme
  const nftColors = {
    gradient: "from-[#4B0082] to-[#8A2BE2]",
    bg: "bg-[#4B0082]/10",
    text: "text-[#4B0082]",
    highlight: "text-[#4B0082]",
    hover: "hover:text-[#4B0082]",
    ring: "[#4B0082]",
    hoverBg: "[#4B0082]",
  };

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <CategoryDashboard
        coins={nftCoins}
        categoryId="nft"
        title="NFT Crypto Market Overview"
        colors={nftColors}
      />

      {/* Coin List Table */}
      <CoinListTable
        coins={nftCoins}
        categoryId="nft"
        title="Cryptocurrency Prices by Market Cap"
        colors={nftColors}
      />
    </div>
  );
};

export default NftCoins;
