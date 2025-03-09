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
  const [investmentFees, setInvestmentFees] = useState("1");
  const [exitFees, setExitFees] = useState("1");

  const tokens = [
    { symbol: "BTC", name: "Bitcoin" },
    { symbol: "ETH", name: "Ethereum" },
    { symbol: "SOL", name: "Solana" },
    { symbol: "ADA", name: "Cardano" },
    { symbol: "XRP", name: "Ripple" },
  ];

  const currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"];

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
        {activeCalculator === "roi" ? (
          <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-teal-600 to-teal-700 text-white p-4 font-medium flex items-center">
              <BarChart2 size={20} className="mr-2" />
              <span>ROI Calculator</span>
            </div>
            <div className="p-5"></div>

            {/* Results Panel - Now below the calculator instead of to the right */}
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
