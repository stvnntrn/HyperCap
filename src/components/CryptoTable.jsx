import { useState } from "react";
import { Search } from "lucide-react";
import TableHeader from "./TableHeader";
import CoinListItem from "./CoinListItem";

const CryptoTable = ({
  coins,
  searchPlaceholder = "Search coins...",
  gradientColors = "from-[#1A1A3A] to-[#4A4AFF]",
  getTrendIndicator,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortConfig, setSortConfig] = useState({
    key: "marketCap",
    direction: "desc",
  });

  // Get market cap ranking map
  const getMarketCapRanking = () => {
    const sortedByMarketCap = [...coins].sort(
      (a, b) => b.marketCap - a.marketCap
    );
    return new Map(
      sortedByMarketCap.map((coin, index) => [coin.id, index + 1])
    );
  };

  // Handle sorting
  const handleSort = (key) => {
    setSortConfig((prevConfig) => ({
      key,
      direction:
        prevConfig.key === key && prevConfig.direction === "desc"
          ? "asc"
          : "desc",
    }));
  };

  // Get filtered and sorted coins
  const getFilteredAndSortedCoins = () => {
    let filteredCoins = [...coins];

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filteredCoins = filteredCoins.filter(
        (coin) =>
          coin.name.toLowerCase().includes(query) ||
          coin.symbol.toLowerCase().includes(query)
      );
    }

    // Apply sorting
    if (sortConfig.key) {
      filteredCoins.sort((a, b) => {
        let aValue =
          sortConfig.key === "coin" ? a.name.toLowerCase() : a[sortConfig.key];
        let bValue =
          sortConfig.key === "coin" ? b.name.toLowerCase() : b[sortConfig.key];

        if (sortConfig.direction === "asc") {
          return aValue > bValue ? 1 : -1;
        }
        return aValue < bValue ? 1 : -1;
      });
    }

    return filteredCoins;
  };

  const marketCapRanking = getMarketCapRanking();

  return (
    <div className="overflow-hidden rounded-xl">
      {/* Search bar */}
      <div className="mb-4 flex justify-between items-center">
        <div className="relative">
          <input
            type="text"
            placeholder={searchPlaceholder}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-4 py-1.5 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-[#1A1A3A] focus:border-transparent text-sm"
          />
          <Search
            size={16}
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
          />
        </div>
      </div>

      {/* Table */}
      <table className="min-w-full table-fixed">
        <TableHeader
          sortConfig={sortConfig}
          onSort={handleSort}
          gradientColors={gradientColors}
        />
        <tbody className="divide-y divide-gray-200 bg-white">
          {getFilteredAndSortedCoins().map((coin) => (
            <CoinListItem
              key={coin.id}
              coin={coin}
              rank={marketCapRanking.get(coin.id)}
              getTrendIndicator={getTrendIndicator}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CryptoTable;
