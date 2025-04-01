import { Star, TrendingUp, TrendingDown } from "lucide-react";
import { formatNumber, formatCompactNumber } from "../utils/formatNumber";

const CoinListItem = ({ coin, rank, getTrendIndicator }) => {
  return (
    <tr className="hover:bg-[#1A1A3A]/10 transition-colors cursor-pointer">
      <td className="py-4 pl-3 whitespace-nowrap text-sm font-medium text-gray-700 w-0">
        <Star size={16} className="text-gray-400 hover:text-[#1A1A3A]" />
      </td>
      <td className="py-4 pl-5 whitespace-nowrap text-sm font-medium text-gray-700 max-w-[28px]">
        {rank}
      </td>
      <td className="py-4 pl-7 whitespace-nowrap">
        <div className="flex items-center">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[#1A1A3A] to-[#4A4AFF] flex items-center justify-center text-white font-bold mr-3 shadow-md">
            {coin.symbol.charAt(0)}
          </div>
          <div className="flex items-center gap-2">
            <div className="font-medium">{coin.name}</div>
            <div className="text-gray-500 text-sm">{coin.symbol}</div>
          </div>
        </div>
      </td>
      <td className="py-4 text-right whitespace-nowrap font-medium w-0">
        {formatNumber(coin.price)}
      </td>
      <td className="py-4 pl-9 text-right whitespace-nowrap w-0">
        <span className="flex items-center justify-end">
          {coin.change1h >= 0 ? (
            <TrendingUp size={14} className="mr-1 text-green-500" />
          ) : (
            <TrendingDown size={14} className="mr-1 text-red-500" />
          )}
          <span
            className={coin.change1h >= 0 ? "text-green-500" : "text-red-500"}
          >
            {coin.change1h >= 0 ? "+" : ""}
            {coin.change1h}%
          </span>
        </span>
      </td>
      <td className="py-4 pl-9 text-right whitespace-nowrap w-0">
        <span className="flex items-center justify-end">
          {coin.change24h >= 0 ? (
            <TrendingUp size={14} className="mr-1 text-green-500" />
          ) : (
            <TrendingDown size={14} className="mr-1 text-red-500" />
          )}
          <span
            className={coin.change24h >= 0 ? "text-green-500" : "text-red-500"}
          >
            {coin.change24h >= 0 ? "+" : ""}
            {coin.change24h}%
          </span>
        </span>
      </td>
      <td className="py-4 pl-9 text-right whitespace-nowrap w-0">
        <span className="flex items-center justify-end">
          {coin.change7d >= 0 ? (
            <TrendingUp size={14} className="mr-1 text-green-500" />
          ) : (
            <TrendingDown size={14} className="mr-1 text-red-500" />
          )}
          <span
            className={coin.change7d >= 0 ? "text-green-500" : "text-red-500"}
          >
            {coin.change7d >= 0 ? "+" : ""}
            {coin.change7d}%
          </span>
        </span>
      </td>
      <td className="py-4 pl-9 text-right whitespace-nowrap w-0">
        {formatCompactNumber(coin.volume)}
      </td>
      <td className="py-4 pl-9 text-right whitespace-nowrap w-0">
        {formatCompactNumber(coin.marketCap)}
      </td>
      <td className="pr-4 pl-4 text-right w-0">
        <div className="rounded-md p-1 flex justify-end">
          {getTrendIndicator(coin.change7d)}
        </div>
      </td>
    </tr>
  );
};

export default CoinListItem;
