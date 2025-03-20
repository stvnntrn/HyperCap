import { useState } from "react";
import { ArrowUpDown, Repeat } from "lucide-react";
import { coins } from "../data/coins";

const Converter = () => {
  const [fromAmount, setFromAmount] = useState("");
  const [toAmount, setToAmount] = useState("");
  const [fromType, setFromType] = useState("USD");
  const [toType, setToType] = useState("BTC");

  const currencies = ["AUD", "CAD", "EUR", "GBP", "JPY", "USD"];
  const allOptions = [
    ...currencies,
    ...coins.map((coin) => coin.symbol),
  ].sort();

  // Get currency symbol
  const getCurrencySymbol = (curr) => {
    switch (curr) {
      case "USD":
        return "$";
      case "EUR":
        return "€";
      case "GBP":
        return "£";
      case "JPY":
        return "¥";
      case "CAD":
        return "C$";
      case "AUD":
        return "A$";
      default:
        return curr;
    }
  };

  // Get the price in USD for any symbol
  const getUSDPrice = (symbol) => {
    if (currencies.includes(symbol)) {
      switch (symbol) {
        case "USD":
          return 1;
        case "EUR":
          return 1.08;
        case "GBP":
          return 1.26;
        case "JPY":
          return 0.0067;
        case "CAD":
          return 0.74;
        case "AUD":
          return 0.65;
        default:
          return 1;
      }
    }
    const coin = coins.find((c) => c.symbol === symbol);
    return coin ? coin.price : 0;
  };

  // Convert between any two symbols
  const convert = (amount, from, to) => {
    const fromUSD = getUSDPrice(from);
    const toUSD = getUSDPrice(to);
    return (amount * fromUSD) / toUSD;
  };

  // Handle amount changes
  const handleFromAmountChange = (value) => {
    setFromAmount(value);
    if (value === "") {
      setToAmount("");
    } else {
      const converted = convert(parseFloat(value), fromType, toType);
      setToAmount(converted.toFixed(8));
    }
  };

  const handleToAmountChange = (value) => {
    setToAmount(value);
    if (value === "") {
      setFromAmount("");
    } else {
      const converted = convert(parseFloat(value), toType, fromType);
      setFromAmount(converted.toFixed(8));
    }
  };

  // Swap currencies
  const handleSwap = () => {
    setFromType(toType);
    setToType(fromType);
    setFromAmount(toAmount);
    setToAmount(fromAmount);
  };

  // Format display text for options
  const getOptionText = (symbol) => {
    if (currencies.includes(symbol)) {
      return `${symbol} (${getCurrencySymbol(symbol)})`;
    }
    const coin = coins.find((c) => c.symbol === symbol);
    return coin ? `${coin.name} (${coin.symbol})` : symbol;
  };

  // Add this function to measure text width
  const getTextWidth = (text) => {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    context.font = "16px Inter, system-ui, sans-serif";
    const metrics = context.measureText(text);
    return metrics.width;
  };

  const getTokenPadding = (symbol, isToken = false) => {
    const symbolText = isToken ? symbol : getCurrencySymbol(symbol);
    const textWidth = getTextWidth(symbolText);

    if (isToken) {
      const grayBoxPadding = 18;
      const spacingAfterBox = 14;
      return `${Math.max(40, textWidth + grayBoxPadding + spacingAfterBox)}px`;
    } else {
      const grayBoxPadding = 18;
      const spacingAfterBox = 14;
      const extraPadding = symbolText.length > 1 ? 4 : 0;
      return `${Math.max(
        36,
        textWidth + grayBoxPadding + spacingAfterBox + extraPadding
      )}px`;
    }
  };

  return (
    <div className="container mx-auto px-4 mt-8 mb-16">
      <div className="flex flex-col items-center p-6 text-center">
        <div className="bg-teal-100 p-3 rounded-xl mb-4">
          <ArrowUpDown size={40} className="text-teal-600" />
        </div>
        <h1 className="text-4xl font-bold mb-2 text-gray-900">Converter</h1>
        <p className="text-gray-600 font-bold text-base mx-auto max-w-sm">
          Convert between cryptocurrencies and fiat currencies instantly
        </p>
      </div>

      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
          <div className="bg-teal-700 text-white p-4 font-medium flex items-center">
            <Repeat size={20} className="mr-2" />
            <span>Convert</span>
          </div>

          <div className="p-5">
            <div className="grid grid-cols-1">
              {/* From Amount */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                  From
                </label>
                <div className="grid grid-cols-3 gap-4">
                  <div className="col-span-2">
                    <div className="relative rounded-lg shadow-sm">
                      <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                        <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                          {currencies.includes(fromType)
                            ? getCurrencySymbol(fromType)
                            : fromType}
                        </span>
                      </div>
                      <input
                        type="number"
                        value={fromAmount}
                        onChange={(e) => handleFromAmountChange(e.target.value)}
                        placeholder="0.00"
                        className="block w-full pr-3 py-2 rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                        style={{
                          paddingLeft: getTokenPadding(
                            fromType,
                            !currencies.includes(fromType)
                          ),
                        }}
                      />
                    </div>
                  </div>
                  <div className="col-span-1">
                    <select
                      value={fromType}
                      onChange={(e) => setFromType(e.target.value)}
                      className="w-full rounded-lg border-r-8 border-transparent outline outline-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                    >
                      {allOptions.map((symbol) => (
                        <option key={symbol} value={symbol}>
                          {getOptionText(symbol)}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Swap Button */}
              <div className="flex justify-center">
                <button
                  onClick={handleSwap}
                  className="p-2 rounded-full hover:bg-gray-100 transition-colors"
                >
                  <ArrowUpDown size={24} className="text-teal-600" />
                </button>
              </div>

              {/* To Amount */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                  To
                </label>
                <div className="grid grid-cols-3 gap-4">
                  <div className="col-span-2">
                    <div className="relative rounded-lg shadow-sm">
                      <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                        <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                          {currencies.includes(toType)
                            ? getCurrencySymbol(toType)
                            : toType}
                        </span>
                      </div>
                      <input
                        type="number"
                        value={toAmount}
                        onChange={(e) => handleToAmountChange(e.target.value)}
                        placeholder="0.00"
                        className="block w-full pr-3 py-2 rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                        style={{
                          paddingLeft: getTokenPadding(
                            toType,
                            !currencies.includes(toType)
                          ),
                        }}
                      />
                    </div>
                  </div>
                  <div className="col-span-1">
                    <select
                      value={toType}
                      onChange={(e) => setToType(e.target.value)}
                      className="w-full rounded-lg border-r-8 border-transparent outline outline-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                    >
                      {allOptions.map((symbol) => (
                        <option key={symbol} value={symbol}>
                          {getOptionText(symbol)}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Exchange Rate Display */}
              <div className="mt-4">
                <p className="text-sm text-gray-600 text-center">
                  1 {fromType} = {convert(1, fromType, toType).toFixed(8)}{" "}
                  {toType}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Converter;
