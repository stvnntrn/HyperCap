import { ArrowUp, ArrowDown } from "lucide-react";

const TableHeader = ({ sortConfig, onSort, gradientColors }) => {
  const handleSort = (key) => {
    onSort(key);
  };

  return (
    <thead className={`bg-gradient-to-r ${gradientColors}`}>
      <tr>
        <th className="py-4 pl-3 whitespace-nowrap text-sm font-medium text-white w-0"></th>
        <th className="py-4 pl-5 text-left text-xs font-medium text-white uppercase tracking-wider w-0">
          <div className="flex items-center gap-1">
            <span className="text-white">#</span>
          </div>
        </th>
        <th className="py-4 pl-7 text-left text-xs font-medium text-white uppercase tracking-wider">
          <div className="flex items-center gap-1">
            <span
              className="cursor-pointer hover:text-blue-200 transition-colors"
              onClick={() => handleSort("coin")}
            >
              Coin
            </span>
            {sortConfig.key === "coin" &&
              (sortConfig.direction === "desc" ? (
                <ArrowDown size={14} />
              ) : (
                <ArrowUp size={14} />
              ))}
          </div>
        </th>
        <th className="py-4 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
          <div className="flex items-center justify-end gap-1">
            <span
              className="cursor-pointer hover:text-blue-200 transition-colors"
              onClick={() => handleSort("price")}
            >
              Price
            </span>
            {sortConfig.key === "price" &&
              (sortConfig.direction === "desc" ? (
                <ArrowDown size={14} />
              ) : (
                <ArrowUp size={14} />
              ))}
          </div>
        </th>
        <th className="py-4 pl-9 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
          <div className="flex items-center justify-end gap-1">
            <span
              className="cursor-pointer hover:text-blue-200 transition-colors"
              onClick={() => handleSort("change1h")}
            >
              1h %
            </span>
            {sortConfig.key === "change1h" &&
              (sortConfig.direction === "desc" ? (
                <ArrowDown size={14} />
              ) : (
                <ArrowUp size={14} />
              ))}
          </div>
        </th>
        <th className="py-4 pl-9 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
          <div className="flex items-center justify-end gap-1">
            <span
              className="cursor-pointer hover:text-blue-200 transition-colors"
              onClick={() => handleSort("change24h")}
            >
              24h %
            </span>
            {sortConfig.key === "change24h" &&
              (sortConfig.direction === "desc" ? (
                <ArrowDown size={14} />
              ) : (
                <ArrowUp size={14} />
              ))}
          </div>
        </th>
        <th className="py-4 pl-9 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
          <div className="flex items-center justify-end gap-1">
            <span
              className="cursor-pointer hover:text-blue-200 transition-colors"
              onClick={() => handleSort("change7d")}
            >
              7d %
            </span>
            {sortConfig.key === "change7d" &&
              (sortConfig.direction === "desc" ? (
                <ArrowDown size={14} />
              ) : (
                <ArrowUp size={14} />
              ))}
          </div>
        </th>
        <th className="py-4 pl-9 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
          <div className="flex items-center justify-end gap-1">
            <span
              className="cursor-pointer hover:text-blue-200 transition-colors"
              onClick={() => handleSort("volume")}
            >
              Volume
            </span>
            {sortConfig.key === "volume" &&
              (sortConfig.direction === "desc" ? (
                <ArrowDown size={14} />
              ) : (
                <ArrowUp size={14} />
              ))}
          </div>
        </th>
        <th className="py-4 pl-9 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
          <div className="flex items-center justify-end gap-1">
            <span
              className="cursor-pointer hover:text-blue-200 transition-colors"
              onClick={() => handleSort("marketCap")}
            >
              Market Cap
            </span>
            {sortConfig.key === "marketCap" &&
              (sortConfig.direction === "desc" ? (
                <ArrowDown size={14} />
              ) : (
                <ArrowUp size={14} />
              ))}
          </div>
        </th>
        <th className="py-4 pr-4 text-right text-xs font-medium text-white uppercase tracking-wider w-0">
          <span>Last 7 Days</span>
        </th>
      </tr>
    </thead>
  );
};

export default TableHeader;
