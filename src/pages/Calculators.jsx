import { useState } from "react";
import { Calculator, TrendingUp, Coins } from "lucide-react";

const Calculators = () => {
  const [activeCalculator, setActiveCalculator] = useState("roi");

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

      {activeCalculator === "roi" ? (
        <div>ROI Calculator</div>
      ) : (
        <div>Staking Calculator</div>
      )}
    </div>
  );
};

export default Calculators;
