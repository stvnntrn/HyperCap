import { useState } from "react";
import {
  Calculator,
  TrendingUp,
  Coins,
  DollarSign,
  Percent,
  ArrowDown,
  BarChart2,
} from "lucide-react";

const Calculators = () => {
  const [activeCalculator, setActiveCalculator] = useState("roi");
  const [currency, setCurrency] = useState("USD");
  const [amount, setAmount] = useState("");
  const [token, setToken] = useState("BTC");
  const [buyPrice, setBuyPrice] = useState("");
  const [sellPrice, setSellPrice] = useState("");
  const [investmentFees, setInvestmentFees] = useState("");
  const [exitFees, setExitFees] = useState("");

  const tokens = [
    { symbol: "BTC", name: "Bitcoin" },
    { symbol: "ETH", name: "Ethereum" },
    { symbol: "SOL", name: "Solana" },
    { symbol: "ADA", name: "Cardano" },
    { symbol: "XRP", name: "Ripple" },
  ];

  const currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"];

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
        return "$";
    }
  };

  return (
    <div className="container mx-auto px-4 max-w-3xl mt-8">
      <div className="flex flex-col items-center p-6 text-center">
        <div className="bg-teal-100 p-3 rounded-xl mb-4">
          <Calculator size={40} className="text-teal-600" />
        </div>

        <h1 className="text-4xl font-bold mb-2 text-gray-900">
          Calculate Potential Rewards
        </h1>

        <p className="text-gray-600 font-bold text-base mx-auto max-w-sm">
          Plan your investments and see potential returns at a glance
        </p>
      </div>

      {/* Tabs */}
      <div className="flex mb-6 bg-gray-100 p-1 rounded-full w-fit mx-auto">
        <button
          onClick={() => setActiveCalculator("roi")}
          className={`flex items-center px-6 py-3 rounded-full text-sm transition-all ${
            activeCalculator === "roi"
              ? "bg-gradient-to-r from-teal-600 to-teal-700 text-white shadow-md"
              : "text-gray-600 hover:bg-gray-200"
          }`}
        >
          <TrendingUp
            size={18}
            className={`mr-2 ${
              activeCalculator === "roi" ? "text-white" : "text-teal-600"
            }`}
          />
          ROI Calculator
        </button>
        <button
          onClick={() => setActiveCalculator("staking")}
          className={`flex items-center px-6 py-3 rounded-full text-sm transition-all ${
            activeCalculator === "staking"
              ? "bg-gradient-to-r from-teal-600 to-teal-700 text-white shadow-md"
              : "text-gray-600 hover:bg-gray-200"
          }`}
        >
          <Coins
            size={18}
            className={`mr-2 ${
              activeCalculator === "staking" ? "text-white" : "text-teal-600"
            }`}
          />
          Staking Calculator
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Calculator panel roi calculator */}
        {activeCalculator === "roi" ? (
          <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-4 font-medium flex items-center">
              <BarChart2 size={20} className="mr-2" />
              <span>ROI Calculator</span>
            </div>

            <div className="grid grid-cols-4 gap-4 p-5">
              {/* Token Selection */}
              <div className="col-span-4">
                <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                  Token
                </label>
                <select
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                >
                  {tokens.map((t) => (
                    <option key={t.symbol} value={t.symbol}>
                      {t.name} ({t.symbol})
                    </option>
                  ))}
                </select>
              </div>

              {/* Currency Selection */}
              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                  Currency
                </label>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                >
                  {currencies.map((curr) => (
                    <option key={curr} value={curr}>
                      {curr}
                    </option>
                  ))}
                </select>
              </div>

              {/* Amount */}
              <div className="col-span-3">
                <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                  Total Investment
                </label>
                <div className="relative rounded-lg shadow-sm">
                  <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                    <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                      {getCurrencySymbol(currency)}
                    </span>
                  </div>
                  <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pl-11 pr-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Buy Price */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Entry Price ({currency})
                </label>
                <div className="relative rounded-lg shadow-sm">
                  <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                    <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                      {getCurrencySymbol(currency)}
                    </span>
                  </div>
                  <input
                    type="number"
                    value={buyPrice}
                    onChange={(e) => setBuyPrice(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pl-11 pr-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Entry Fee */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Entry Fee ({currency})
                </label>
                <div className="relative rounded-lg shadow-sm">
                  <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                    <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                      {getCurrencySymbol(currency)}
                    </span>
                  </div>
                  <input
                    type="number"
                    value={investmentFees}
                    onChange={(e) => setInvestmentFees(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pl-11 pr-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Sell Price */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sell Price ({currency})
                </label>
                <div className="relative rounded-lg shadow-sm">
                  <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                    <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                      {getCurrencySymbol(currency)}
                    </span>
                  </div>
                  <input
                    type="number"
                    value={sellPrice}
                    onChange={(e) => setSellPrice(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pl-11 pr-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Exit Fee */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Exit Fee ({currency})
                </label>
                <div className="relative rounded-lg shadow-sm">
                  <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                    <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                      {getCurrencySymbol(currency)}
                    </span>
                  </div>
                  <input
                    type="number"
                    value={exitFees}
                    onChange={(e) => setExitFees(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pl-11 pr-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Results Panel for roi calculator */}
            <div className="border-t border-gray-200">
              <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-4 font-medium flex items-center">
                <BarChart2 size={20} className="mr-2" />
                <span>Investment Results</span>
              </div>
              <div className="p-5 bg-gray-50"></div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-4 font-medium flex items-center">
              <BarChart2 size={20} className="mr-2" />
              <span>Staking Calculator</span>
            </div>
            <div className="p-5"></div>

            {/* Results Panel for staking calculator */}
            <div className="border-t border-gray-200">
              <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-4 font-medium flex items-center">
                <BarChart2 size={20} className="mr-2" />
                <span>Investment Results</span>
              </div>
              <div className="p-5 bg-gray-50"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Calculators;
