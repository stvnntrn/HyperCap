import { useState, useEffect, useRef } from "react";
import { coins } from "../data/coins";
import { Search, ArrowDown, X } from "lucide-react";

const Compare = () => {
  const [coin1, setCoin1] = useState("");
  const [coin2, setCoin2] = useState("");
  const [searchQuery1, setSearchQuery1] = useState("");
  const [searchQuery2, setSearchQuery2] = useState("");
  const [showDropdown1, setShowDropdown1] = useState(false);
  const [showDropdown2, setShowDropdown2] = useState(false);
  const dropdownRef1 = useRef(null);
  const dropdownRef2 = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef1.current &&
        !dropdownRef1.current.contains(event.target)
      ) {
        setShowDropdown1(false);
      }
      if (
        dropdownRef2.current &&
        !dropdownRef2.current.contains(event.target)
      ) {
        setShowDropdown2(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Filter coins based on search query
  const filteredCoins1 = coins.filter(
    (coin) =>
      coin.name.toLowerCase().includes(searchQuery1.toLowerCase()) ||
      coin.symbol.toLowerCase().includes(searchQuery1.toLowerCase())
  );

  const filteredCoins2 = coins.filter(
    (coin) =>
      coin.name.toLowerCase().includes(searchQuery2.toLowerCase()) ||
      coin.symbol.toLowerCase().includes(searchQuery2.toLowerCase())
  );

  // Get selected coin data
  const selectedCoin1 = coins.find((coin) => coin.id === coin1);
  const selectedCoin2 = coins.find((coin) => coin.id === coin2);

  return (
    <div className="container mx-auto bg-white text-gray-800 p-6 rounded-xl">
      <h1 className="text-3xl font-bold mb-8 text-center">
        Cryptocurrency Comparison Tool
      </h1>

      <div className="grid grid-cols-2 gap-8 max-w-4xl mx-auto">
        {/* First Coin Selector */}
        <div className="relative" ref={dropdownRef1}>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select First Coin
          </label>
          <div className="relative">
            <div
              onClick={() => {
                if (!showDropdown1 && !searchQuery1) {
                  setCoin1("");
                }
                setShowDropdown1(!showDropdown1);
              }}
              className="w-full p-3 border border-gray-300 rounded-lg cursor-pointer flex items-center justify-between hover:border-gray-400 transition-colors"
            >
              {showDropdown1 ? (
                <div className="relative w-full">
                  <Search
                    size={16}
                    className="absolute left-0 top-1/2 transform -translate-y-1/2 text-gray-400"
                  />
                  <input
                    type="text"
                    placeholder="Search coins..."
                    value={searchQuery1}
                    onChange={(e) => {
                      setSearchQuery1(e.target.value);
                      if (!e.target.value) {
                        setCoin1("");
                      }
                    }}
                    onClick={(e) => e.stopPropagation()}
                    onDoubleClick={(e) => e.stopPropagation()}
                    className="w-full pl-6 pr-4 focus:outline-none"
                    autoFocus
                  />
                </div>
              ) : selectedCoin1 ? (
                <div className="flex items-center gap-2 w-full">
                  <div className="h-6 w-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-xs">
                    {selectedCoin1.symbol.charAt(0)}
                  </div>
                  <span className="flex-grow">{selectedCoin1.name}</span>
                </div>
              ) : (
                <span className="text-gray-700">Select a coin</span>
              )}
              {selectedCoin1 ? (
                <X
                  size={16}
                  className="text-gray-400 hover:text-gray-600 cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    setCoin1("");
                    setSearchQuery1("");
                  }}
                />
              ) : (
                <ArrowDown size={16} className="text-gray-400" />
              )}
            </div>
            {showDropdown1 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto">
                <div className="py-1">
                  {filteredCoins1.map((coin) => (
                    <div
                      key={coin.id}
                      onClick={() => {
                        setCoin1(coin.id);
                        setShowDropdown1(false);
                      }}
                      className="flex items-center gap-2 px-4 py-2 hover:bg-gray-100 cursor-pointer"
                    >
                      <div className="h-6 w-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-xs">
                        {coin.symbol.charAt(0)}
                      </div>
                      <div>
                        <div className="font-medium">{coin.name}</div>
                        <div className="text-sm text-gray-500">
                          {coin.symbol}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Second Coin Selector */}
        <div className="relative" ref={dropdownRef2}>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Second Coin
          </label>
          <div className="relative">
            <div
              onClick={() => {
                if (!showDropdown2 && !searchQuery2) {
                  setCoin2("");
                }
                setShowDropdown2(!showDropdown2);
              }}
              className="w-full p-3 border border-gray-300 rounded-lg cursor-pointer flex items-center justify-between hover:border-gray-400 transition-colors"
            >
              {showDropdown2 ? (
                <div className="relative w-full">
                  <Search
                    size={16}
                    className="absolute left-0 top-1/2 transform -translate-y-1/2 text-gray-400"
                  />
                  <input
                    type="text"
                    placeholder="Search coins..."
                    value={searchQuery2}
                    onChange={(e) => {
                      setSearchQuery2(e.target.value);
                      if (!e.target.value) {
                        setCoin2("");
                      }
                    }}
                    onClick={(e) => e.stopPropagation()}
                    onDoubleClick={(e) => e.stopPropagation()}
                    className="w-full pl-6 pr-4 focus:outline-none"
                    autoFocus
                  />
                </div>
              ) : selectedCoin2 ? (
                <div className="flex items-center gap-2 w-full">
                  <div className="h-6 w-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-xs">
                    {selectedCoin2.symbol.charAt(0)}
                  </div>
                  <span className="flex-grow">{selectedCoin2.name}</span>
                </div>
              ) : (
                <span className="text-gray-700">Select a coin</span>
              )}
              {selectedCoin2 ? (
                <X
                  size={16}
                  className="text-gray-400 hover:text-gray-600 cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    setCoin2("");
                    setSearchQuery2("");
                  }}
                />
              ) : (
                <ArrowDown size={16} className="text-gray-400" />
              )}
            </div>
            {showDropdown2 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto">
                <div className="py-1">
                  {filteredCoins2.map((coin) => (
                    <div
                      key={coin.id}
                      onClick={() => {
                        setCoin2(coin.id);
                        setShowDropdown2(false);
                      }}
                      className="flex items-center gap-2 px-4 py-2 hover:bg-gray-100 cursor-pointer"
                    >
                      <div className="h-6 w-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-xs">
                        {coin.symbol.charAt(0)}
                      </div>
                      <div>
                        <div className="font-medium">{coin.name}</div>
                        <div className="text-sm text-gray-500">
                          {coin.symbol}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Compare;
