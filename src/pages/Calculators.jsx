/* eslint-disable react-hooks/exhaustive-deps */
import { useState, useEffect } from "react";
import { coins } from "../data/coins";
import {
  Calculator,
  TrendingUp,
  Coins,
  BarChart2,
  ArrowUp,
  ArrowDown,
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
  const [calculationResult, setCalculationResult] = useState(null);

  // Staking calculator states
  const [stakingAmount, setStakingAmount] = useState("");
  const [isTokenAmount, setIsTokenAmount] = useState(false);
  const [stakingRate, setStakingRate] = useState("");
  const [isAPR, setIsAPR] = useState(true);
  const [stakingDuration, setStakingDuration] = useState("");
  const [durationUnit, setDurationUnit] = useState("days");
  const [compoundingFrequency, setCompoundingFrequency] = useState("daily");
  const [useCurrentPrice, setUseCurrentPrice] = useState(true);
  const [customTokenPrice, setCustomTokenPrice] = useState("");

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

  useEffect(() => {
    calculateResults();
  }, [amount, buyPrice, investmentFees, sellPrice, exitFees, currency, token]);

  const calculateResults = () => {
    const investmentAmount = parseFloat(amount) || 0;
    const entryPrice = parseFloat(buyPrice) || 0;
    const entryFee = parseFloat(investmentFees) || 0;
    const exitPrice = parseFloat(sellPrice) || 0;
    const exitFee = parseFloat(exitFees) || 0;

    // Calculate total investment
    const totalInvestment = investmentAmount + entryFee;
    const tokensPurchased = entryPrice > 0 ? investmentAmount / entryPrice : 0;

    // Calculate exit amount
    const grossReturn = tokensPurchased * exitPrice;
    const netReturn = grossReturn - exitFee;

    // Calculate profit/loss (only if both prices are provided)
    const hasBothPrices = Boolean(buyPrice && sellPrice);
    const absoluteProfit = hasBothPrices ? netReturn - totalInvestment : 0;
    const percentageReturn =
      hasBothPrices && totalInvestment > 0
        ? ((netReturn - totalInvestment) / totalInvestment) * 100
        : 0;

    // Calculate total fees
    const totalFees = entryFee + exitFee;

    setCalculationResult({
      tokensPurchased,
      totalInvestment,
      grossReturn,
      netReturn,
      absoluteProfit,
      percentageReturn,
      totalFees,
      isProfit: absoluteProfit >= 0,
    });
  };

  // Format currency
  const formatCurrency = (value, currency) => {
    const numValue = parseFloat(value);

    if (numValue >= 1000000000) {
      // For billions
      const valueInB = numValue / 1000000000;
      if (valueInB % 1 === 0) {
        return `${getCurrencySymbol(currency)}${valueInB.toFixed(0)}B`;
      } else {
        return `${getCurrencySymbol(currency)}${valueInB.toFixed(1)}B`;
      }
    } else if (numValue >= 1000000) {
      // For millions
      const valueInM = numValue / 1000000;
      if (valueInM % 1 === 0) {
        return `${getCurrencySymbol(currency)}${valueInM.toFixed(0)}M`;
      } else {
        return `${getCurrencySymbol(currency)}${valueInM.toFixed(1)}M`;
      }
    } else if (numValue >= 10000) {
      // For thousands
      const valueInK = numValue / 1000;
      if (valueInK % 1 === 0) {
        return `${getCurrencySymbol(currency)}${valueInK.toFixed(0)}K`;
      } else {
        return `${getCurrencySymbol(currency)}${valueInK.toFixed(1)}K`;
      }
    } else {
      return `${getCurrencySymbol(currency)}${numValue.toFixed(2)}`;
    }
  };

  return (
    <div className="container mx-auto px-4 mt-8">
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

      {/* Calculator panel roi calculator */}
      {activeCalculator === "roi" ? (
        <div className="grid grid-cols-3 gap-4 max-w-5xl mx-auto">
          <div className="col-span-2 bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden ">
            <div className="bg-teal-700 text-white p-4 font-medium flex items-center">
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
                  {coins.map((t) => (
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
          </div>

          {/* Investment results */}
          {calculationResult && (
            <div className="col-span-1 bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div className="bg-teal-700 text-white p-4 font-medium flex items-center">
                <TrendingUp size={20} className="mr-2" />
                <span>Investment Results</span>
              </div>

              <div className="pl-5 pt-1.5">
                <div className="divide-y divide-gray-200">
                  {/* Profit/Loss */}
                  <div className="py-3 first:pt-2">
                    <div className="text-lg text-gray-500 mb-2">
                      Profit/Loss
                    </div>
                    <div className="flex items-center">
                      <span
                        className={`text-2xl font-bold ${
                          !buyPrice || !sellPrice
                            ? "text-gray-600"
                            : calculationResult.isProfit
                            ? "text-green-600"
                            : "text-red-600"
                        }`}
                      >
                        {!buyPrice || !sellPrice ? (
                          formatCurrency(0)
                        ) : calculationResult.isProfit ? (
                          <>
                            <ArrowUp size={26} className="inline mr-2" />
                            {formatCurrency(
                              Math.abs(calculationResult.absoluteProfit)
                            )}
                          </>
                        ) : (
                          <>
                            <ArrowDown size={26} className="inline mr-2" />
                            {formatCurrency(
                              Math.abs(calculationResult.absoluteProfit)
                            )}
                          </>
                        )}
                      </span>
                      <span
                        className={`ml-2 px-2 py-1 rounded-md text-base font-medium ${
                          !buyPrice || !sellPrice
                            ? "bg-gray-100 text-gray-800"
                            : calculationResult.isProfit
                            ? "bg-green-100 text-green-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {!buyPrice || !sellPrice
                          ? "0.00%"
                          : `${Math.abs(
                              calculationResult.percentageReturn
                            ).toFixed(2)}%`}
                      </span>
                    </div>
                  </div>

                  {/* Total Investment */}
                  <div className="py-3">
                    <div className="text-base text-gray-500 mb-1">
                      Total Investment
                    </div>
                    <div className="text-xl font-bold text-gray-600">
                      {formatCurrency(calculationResult.totalInvestment)}
                    </div>
                  </div>

                  {/* Total Exit Amount */}
                  <div className="py-3">
                    <div className="text-base text-gray-500 mb-1">
                      Total Exit Amount
                    </div>
                    <div className="text-xl font-bold text-gray-600">
                      {formatCurrency(calculationResult.netReturn)}
                    </div>
                  </div>

                  {/* Total Fees */}
                  <div className="py-3 last:pb-2">
                    <div className="text-base text-gray-500 mb-1">
                      Total Fees
                    </div>
                    <div className="text-xl font-bold text-gray-600">
                      {formatCurrency(calculationResult.totalFees)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-3 grid-rows-3 gap-4 mx-auto">
          {/* Staking Calculator */}
          <div className="col-span-3 row-span-1 bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
            <div className="bg-teal-700 text-white p-4 font-medium flex items-center">
              <BarChart2 size={20} className="mr-2" />
              <span>Staking Calculator</span>
            </div>
            <div className="p-5">
              <div className="grid grid-cols-3 gap-6">
                {/* Token and Initial Investment */}
                <div className="space-y-4">
                  {/* Token Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                      Token
                    </label>
                    <select
                      value={token}
                      onChange={(e) => setToken(e.target.value)}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                    >
                      {coins.map((t) => (
                        <option key={t.symbol} value={t.symbol}>
                          {t.name} ({t.symbol})
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Initial Investment */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="block text-sm font-medium text-gray-700 pl-1">
                        Initial Investment
                      </label>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">
                          {currency}
                        </span>
                        <div
                          className="relative w-8 h-4 rounded-full bg-gray-200 cursor-pointer"
                          onClick={() => setIsTokenAmount(!isTokenAmount)}
                        >
                          <div
                            className={`absolute top-0.5 h-3 w-3 rounded-full bg-teal-600 transform transition-transform ease-in-out duration-300 ${
                              isTokenAmount
                                ? "translate-x-4"
                                : "translate-x-0.5"
                            }`}
                          />
                        </div>
                        <span className="text-sm text-gray-600">{token}</span>
                      </div>
                    </div>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                        <span
                          className={`bg-gray-200 text-gray-600 h-full flex items-center rounded-l-lg border-r border-gray-300 ${
                            isTokenAmount ? "px-2 py-2" : "px-3 py-2"
                          }`}
                        >
                          {isTokenAmount ? token : getCurrencySymbol(currency)}
                        </span>
                      </div>
                      <input
                        type="number"
                        value={stakingAmount}
                        onChange={(e) => setStakingAmount(e.target.value)}
                        placeholder="0.00"
                        className={`block w-full ${
                          isTokenAmount ? "pl-14" : "pl-11"
                        } pr-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent`}
                      />
                    </div>
                  </div>
                </div>

                {/* Staking Rate and Duration */}
                <div className="space-y-4">
                  {/* Staking Rate */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                      Staking Rate
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                        <span className="bg-gray-200 text-gray-600 h-full flex items-center rounded-l-lg border-r border-gray-300 px-2 py-2">
                          %
                        </span>
                      </div>
                      <input
                        type="number"
                        value={stakingRate}
                        onChange={(e) => setStakingRate(e.target.value)}
                        placeholder="0.00"
                        className="block w-full pl-11 pr-18 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                      <select
                        value={isAPR ? "APR" : "APY"}
                        onChange={(e) => setIsAPR(e.target.value === "APR")}
                        className="absolute inset-y-0 right-0 w-16 rounded-r-lg border-l border-gray-300 bg-gray-200 text-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent text-center"
                      >
                        <option value="APR">APR</option>
                        <option value="APY">APY</option>
                      </select>
                    </div>
                  </div>

                  {/* Staking Duration */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                      Staking Duration
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                        <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                          #
                        </span>
                      </div>
                      <input
                        type="number"
                        value={stakingDuration}
                        onChange={(e) => setStakingDuration(e.target.value)}
                        placeholder="0"
                        className="block w-full pl-11 pr-22 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                      <select
                        value={durationUnit}
                        onChange={(e) => setDurationUnit(e.target.value)}
                        className="absolute inset-y-0 right-0 w-20 rounded-r-lg border-l border-gray-300 bg-gray-200 text-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent text-center"
                      >
                        <option value="days">Days</option>
                        <option value="months">Months</option>
                        <option value="years">Years</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Compounding and Token Price */}
                <div className="space-y-4">
                  {/* Compounding Frequency */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                      Compounding Frequency
                    </label>
                    <select
                      value={compoundingFrequency}
                      onChange={(e) => setCompoundingFrequency(e.target.value)}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="quarterly">Quarterly</option>
                      <option value="yearly">Yearly</option>
                    </select>
                  </div>

                  {/* Token Price */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="block text-sm font-medium text-gray-700 pl-1">
                        Select {token} Price
                      </label>
                      <div className="flex items-center gap-2">
                        <div
                          className="relative w-8 h-4 rounded-full bg-gray-200 cursor-pointer"
                          onClick={() => setUseCurrentPrice(!useCurrentPrice)}
                        >
                          <div
                            className={`absolute top-0.5 h-3 w-3 rounded-full transform transition-transform ease-in-out duration-300 ${
                              useCurrentPrice
                                ? "translate-x-4 bg-teal-600"
                                : "translate-x-0.5 bg-gray-400"
                            }`}
                          />
                        </div>
                        <span className="text-sm text-gray-600">
                          Current price
                        </span>
                      </div>
                    </div>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                        <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                          {getCurrencySymbol(currency)}
                        </span>
                      </div>
                      <input
                        type="number"
                        value={
                          useCurrentPrice
                            ? coins.find((t) => t.symbol === token).price
                            : customTokenPrice
                        }
                        onChange={(e) => setCustomTokenPrice(e.target.value)}
                        disabled={useCurrentPrice}
                        placeholder="0.00"
                        className={`block w-full pl-11 pr-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent ${
                          useCurrentPrice ? "bg-gray-100" : ""
                        }`}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Investment Chart */}
          <div className="col-span-2 row-span-2 bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
            <div className="bg-teal-700 text-white p-4 font-medium flex items-center">
              <BarChart2 size={20} className="mr-2" />
              <span>Investment Growth</span>
            </div>
            <div className="p-5 h-full">
              {/* Chart */}
              <div className="bg-gray-50 rounded-lg h-full flex items-center justify-center"></div>
            </div>
          </div>

          {/* Staking Returns */}
          <div className="col-span-1 row-span-2 bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
            <div className="bg-teal-700 text-white p-4 font-medium flex items-center">
              <TrendingUp size={20} className="mr-2" />
              <span>Staking Returns</span>
            </div>
            <div className="p-5">
              <div className="divide-y divide-gray-200">
                {/* Daily Staking Returns */}
                <div className="py-5 first:pt-2 last:pb-2">
                  <div className="text-lg text-gray-500 mb-2">
                    Daily Staking Returns
                  </div>
                  <div className="text-3xl font-bold text-gray-600 mb-1">
                    {formatCurrency(0)}
                  </div>
                  <div className="text-base text-gray-500">0.00 {token}</div>
                </div>

                {/* Monthly Staking Returns */}
                <div className="py-5">
                  <div className="text-lg text-gray-500 mb-2">
                    Monthly Staking Returns
                  </div>
                  <div className="text-3xl font-bold text-gray-600 mb-1">
                    {formatCurrency(0)}
                  </div>
                  <div className="text-base text-gray-500">0.00 {token}</div>
                </div>

                {/* Yearly Staking Returns */}
                <div className="py-5 last:pb-2">
                  <div className="text-lg text-gray-500 mb-2">
                    Yearly Staking Returns
                  </div>
                  <div className="text-3xl font-bold text-gray-600 mb-1">
                    {formatCurrency(0)}
                  </div>
                  <div className="text-base text-gray-500">0.00 {token}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Calculators;
