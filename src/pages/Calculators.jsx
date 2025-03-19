/* eslint-disable react-hooks/exhaustive-deps */
import { useState, useEffect } from "react";
import { coins } from "../data/coins";
import { useLocation } from "react-router-dom";
import {
  Calculator,
  TrendingUp,
  Coins,
  BarChart2,
  ArrowUp,
  ArrowDown,
} from "lucide-react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

// ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Calculators = () => {
  const location = useLocation();
  const [activeCalculator, setActiveCalculator] = useState(() => {
    const path = location.pathname;
    if (path.endsWith("/staking")) return "staking";
    if (path.endsWith("/roi")) return "roi";
    return "roi";
  });

  const [roiCurrency, setRoiCurrency] = useState("USD");
  const [stakingCurrency, setStakingCurrency] = useState("USD");
  const [amount, setAmount] = useState("");
  const [token, setToken] = useState("BTC");
  const [buyPrice, setBuyPrice] = useState("");
  const [sellPrice, setSellPrice] = useState("");
  const [investmentFees, setInvestmentFees] = useState("");
  const [exitFees, setExitFees] = useState("");
  const [calculationResult, setCalculationResult] = useState(null);

  const [stakingAmount, setStakingAmount] = useState("");
  const [isTokenAmount, setIsTokenAmount] = useState(false);
  const [stakingRate, setStakingRate] = useState("");
  const [isAPR, setIsAPR] = useState(true);
  const [stakingDuration, setStakingDuration] = useState("");
  const [durationUnit, setDurationUnit] = useState("days");
  const [compoundingFrequency, setCompoundingFrequency] = useState("daily");
  const [useCurrentPrice, setUseCurrentPrice] = useState(true);
  const [customTokenPrice, setCustomTokenPrice] = useState("");

  const [stakingResults, setStakingResults] = useState({
    daily: { fiat: 0, tokens: 0 },
    monthly: { fiat: 0, tokens: 0 },
    yearly: { fiat: 0, tokens: 0 },
    total: { fiat: 0, tokens: 0 },
  });

  const currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"];

  // Add this function to measure text width
  const getTextWidth = (text) => {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    context.font = "16px Inter, system-ui, sans-serif"; // Match your app's font
    const metrics = context.measureText(text);
    return metrics.width;
  };

  const getTokenPadding = (symbol, isToken = false) => {
    const symbolText = isToken ? symbol : getCurrencySymbol(symbol);
    const textWidth = getTextWidth(symbolText);

    if (isToken) {
      // For tokens
      const grayBoxPadding = 14; // 7px on each side
      const spacingAfterBox = 10;
      return `${Math.max(40, textWidth + grayBoxPadding + spacingAfterBox)}px`;
    } else {
      // For currencies
      const grayBoxPadding = 16; // 8px on each side
      const spacingAfterBox = 16;
      const extraPadding = symbolText.length > 1 ? 2 : 0; // Reduced extra padding for multi-character currencies
      return `${Math.max(
        36,
        textWidth + grayBoxPadding + spacingAfterBox + extraPadding
      )}px`;
    }
  };

  const clearStakingInputs = () => {
    setStakingAmount("");
    setIsTokenAmount(false);
    setStakingRate("");
    setIsAPR(true);
    setStakingDuration("");
    setDurationUnit("days");
    setCompoundingFrequency("daily");
    setUseCurrentPrice(true);
    setCustomTokenPrice("");
  };

  const clearROIInputs = () => {
    setAmount("");
    setBuyPrice("");
    setSellPrice("");
    setInvestmentFees("");
    setExitFees("");
  };

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
  }, [
    amount,
    buyPrice,
    investmentFees,
    sellPrice,
    exitFees,
    roiCurrency,
    token,
  ]);

  // Update active calculator when path changes
  useEffect(() => {
    const path = location.pathname;
    if (path.endsWith("/staking")) {
      setActiveCalculator("staking");
    } else if (path.endsWith("/roi")) {
      setActiveCalculator("roi");
    }
  }, [location]);

  useEffect(() => {
    calculateStakingReturns();
  }, [
    stakingAmount,
    stakingRate,
    isAPR,
    compoundingFrequency,
    durationUnit,
    stakingDuration,
    token,
    useCurrentPrice,
    customTokenPrice,
    isTokenAmount,
  ]);

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

  const calculateStakingParameters = () => {
    if (!stakingAmount || !stakingRate || !stakingDuration) {
      return null;
    }

    // Get current market price for token conversion
    const currentMarketPrice = coins.find((t) => t.symbol === token).price;
    const displayPrice = useCurrentPrice
      ? currentMarketPrice
      : parseFloat(customTokenPrice) || 0;

    // Convert input to numbers
    const inputAmount = parseFloat(stakingAmount);
    const principal = isTokenAmount
      ? inputAmount
      : inputAmount / currentMarketPrice;
    const rate = parseFloat(stakingRate) / 100;

    // Convert duration to days
    let durationInDays = parseFloat(stakingDuration);
    if (durationUnit === "months") {
      durationInDays *= 365 / 12;
    } else if (durationUnit === "years") {
      durationInDays *= 365;
    }

    // Calculate compounding periods per year
    let periodsPerYear;
    switch (compoundingFrequency) {
      case "daily":
        periodsPerYear = 365.25;
        break;
      case "weekly":
        periodsPerYear = 52;
        break;
      case "monthly":
        periodsPerYear = 12;
        break;
      case "quarterly":
        periodsPerYear = 4;
        break;
      case "yearly":
        periodsPerYear = 1;
        break;
      default:
        periodsPerYear = 365.25;
    }

    // Calculate APY if APR is given
    let effectiveRate = rate;
    if (isAPR) {
      effectiveRate = Math.pow(1 + rate / periodsPerYear, periodsPerYear) - 1;
    }

    return {
      principal,
      effectiveRate,
      periodsPerYear,
      durationInDays,
      displayPrice,
      currentMarketPrice,
    };
  };

  const calculateStakingReturns = () => {
    const params = calculateStakingParameters();
    if (!params) {
      setStakingResults({
        daily: { fiat: 0, tokens: 0 },
        monthly: { fiat: 0, tokens: 0 },
        yearly: { fiat: 0, tokens: 0 },
        total: { fiat: 0, tokens: 0 },
      });
      return;
    }

    const {
      principal,
      effectiveRate,
      periodsPerYear,
      durationInDays,
      displayPrice,
    } = params;

    // Calculate total returns after the staking period
    const periodsElapsed = durationInDays / (365.25 / periodsPerYear);
    const totalTokens =
      principal * Math.pow(1 + effectiveRate / periodsPerYear, periodsElapsed);
    const totalTokenReturn = totalTokens - principal;

    // Calculate daily returns (average per day over the duration)
    const dailyTokens = totalTokenReturn / durationInDays;

    // Calculate monthly returns (average per month over the duration)
    const monthlyTokens = totalTokenReturn / (durationInDays / 30.44);

    // Calculate yearly returns (average per year over the duration)
    const yearlyTokens = totalTokenReturn / (durationInDays / 365.25);

    // Set results with fiat values calculated using display price
    setStakingResults({
      daily: {
        tokens: dailyTokens,
        fiat: dailyTokens * displayPrice,
      },
      monthly: {
        tokens: monthlyTokens,
        fiat: monthlyTokens * displayPrice,
      },
      yearly: {
        tokens: yearlyTokens,
        fiat: yearlyTokens * displayPrice,
      },
      total: {
        tokens: totalTokenReturn,
        fiat: totalTokenReturn * displayPrice,
      },
    });
  };

  const generateChartData = () => {
    const params = calculateStakingParameters();
    if (!params) {
      return {
        labels: [],
        datasets: [],
      };
    }

    const {
      principal,
      effectiveRate,
      periodsPerYear,
      durationInDays,
      displayPrice,
    } = params;

    // Generate data points
    const dataPoints = [];
    const labels = [];

    // Set fixed number of data points to 20
    const numDataPoints = 20;

    // Calculate step size to ensure we cover the full duration
    const step = durationInDays / (numDataPoints - 1);

    // Generate data points
    for (let i = 0; i < numDataPoints; i++) {
      const currentDay = i * step;
      const periodsElapsed = currentDay / (365.25 / periodsPerYear);
      const balance =
        principal *
        Math.pow(1 + effectiveRate / periodsPerYear, periodsElapsed);
      const rewards = balance - principal;

      dataPoints.push({
        balance: balance * displayPrice,
        rewards: rewards * displayPrice,
      });

      // Format label based on duration unit
      let label;
      if (durationUnit === "days") {
        label = `${Math.round(currentDay)} days`;
      } else if (durationUnit === "months") {
        label = `${Math.round(currentDay / 30.44)} months`;
      } else {
        label = `${Math.round(currentDay / 365.25)} years`;
      }
      labels.push(label);
    }

    // Remove duplicate labels by keeping only unique values
    const uniqueLabels = labels.filter(
      (label, index, self) => self.indexOf(label) === index
    );
    const uniqueDataPoints = uniqueLabels.map((label) => {
      const originalIndex = labels.indexOf(label);
      return dataPoints[originalIndex];
    });

    return {
      labels: uniqueLabels,
      datasets: [
        {
          label: "Total Balance Growth",
          data: uniqueDataPoints.map((point) => point.balance),
          borderColor: "rgb(20, 184, 166)",
          backgroundColor: "rgba(20, 184, 166, 0.1)",
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 6,
        },
      ],
    };
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

  // Get active tab position and width
  const getTabStyle = () => {
    const tabsContainer = document.querySelector("[data-tabs-container]");
    if (!tabsContainer) return { width: "50%", transform: "translateX(0)" };

    const activeTabElement = tabsContainer.querySelector(
      `[data-tab-id="${activeCalculator}"]`
    );
    if (!activeTabElement) return { width: "50%", transform: "translateX(0)" };

    const containerLeft = tabsContainer.getBoundingClientRect().left;
    const tabLeft = activeTabElement.getBoundingClientRect().left;
    const tabWidth = activeTabElement.getBoundingClientRect().width;

    return {
      width: `${tabWidth}px`,
      transform: `translateX(${tabLeft - containerLeft}px)`,
    };
  };

  return (
    <div className="container mx-auto px-4 mt-8 mb-16">
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
      <div
        className="flex mb-6 rounded-full w-fit bg-gray-100/80 backdrop-blur-sm relative mx-auto"
        data-tabs-container
      >
        <div
          className="absolute h-full w-full rounded-full bg-gradient-to-r from-teal-600 to-teal-700 transition-all duration-300 ease-in-out"
          style={getTabStyle()}
        />
        <button
          data-tab-id="roi"
          onClick={() => setActiveCalculator("roi")}
          className={`relative z-10 flex items-center px-6 py-3 rounded-full text-sm transition-all duration-300 ease-in-out cursor-pointer font-semibold ${
            activeCalculator === "roi"
              ? "text-white"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          <TrendingUp
            size={18}
            className={`mr-2 transition-colors duration-300 ${
              activeCalculator === "roi" ? "text-white" : "text-gray-500"
            }`}
          />
          ROI Calculator
        </button>
        <button
          data-tab-id="staking"
          onClick={() => setActiveCalculator("staking")}
          className={`relative z-10 flex items-center px-6 py-3 rounded-full text-sm transition-all duration-300 ease-in-out cursor-pointer font-semibold ${
            activeCalculator === "staking"
              ? "text-white"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          <Coins
            size={18}
            className={`mr-2 transition-colors duration-300 ${
              activeCalculator === "staking" ? "text-white" : "text-gray-500"
            }`}
          />
          Staking Calculator
        </button>
      </div>

      {/* Calculator panel roi calculator */}
      {activeCalculator === "roi" ? (
        <div className="grid grid-cols-3 gap-4 max-w-5xl mx-auto">
          <div className="col-span-2 bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden ">
            <div className="bg-teal-700 text-white p-4 font-medium flex items-center justify-between">
              <div className="flex items-center">
                <BarChart2 size={20} className="mr-2" />
                <span>ROI Calculator</span>
              </div>
              <button
                onClick={clearROIInputs}
                className="px-3 py-1 text-sm bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
              >
                Clear All
              </button>
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
                  className="w-full rounded-lg border-r-8 border-transparent outline outline-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
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
                  value={roiCurrency}
                  onChange={(e) => setRoiCurrency(e.target.value)}
                  className="w-full rounded-lg border-r-8 border-transparent outline outline-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
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
                      {getCurrencySymbol(roiCurrency)}
                    </span>
                  </div>
                  <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pr-3 py-2 rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                    style={{
                      paddingLeft: getTokenPadding(roiCurrency),
                    }}
                  />
                </div>
              </div>

              {/* Buy Price */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Entry Price ({roiCurrency})
                </label>
                <div className="relative rounded-lg shadow-sm">
                  <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                    <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                      {getCurrencySymbol(roiCurrency)}
                    </span>
                  </div>
                  <input
                    type="number"
                    value={buyPrice}
                    onChange={(e) => setBuyPrice(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pr-3 py-2 rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                    style={{
                      paddingLeft: getTokenPadding(roiCurrency),
                    }}
                  />
                </div>
              </div>

              {/* Entry Fee */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Entry Fee ({roiCurrency})
                </label>
                <div className="relative rounded-lg shadow-sm">
                  <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                    <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                      {getCurrencySymbol(roiCurrency)}
                    </span>
                  </div>
                  <input
                    type="number"
                    value={investmentFees}
                    onChange={(e) => setInvestmentFees(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pr-3 py-2 rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                    style={{
                      paddingLeft: getTokenPadding(roiCurrency),
                    }}
                  />
                </div>
              </div>

              {/* Sell Price */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sell Price ({roiCurrency})
                </label>
                <div className="relative rounded-lg shadow-sm">
                  <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                    <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                      {getCurrencySymbol(roiCurrency)}
                    </span>
                  </div>
                  <input
                    type="number"
                    value={sellPrice}
                    onChange={(e) => setSellPrice(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pr-3 py-2 rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                    style={{
                      paddingLeft: getTokenPadding(roiCurrency),
                    }}
                  />
                </div>
              </div>

              {/* Exit Fee */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Exit Fee ({roiCurrency})
                </label>
                <div className="relative rounded-lg shadow-sm">
                  <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                    <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                      {getCurrencySymbol(roiCurrency)}
                    </span>
                  </div>
                  <input
                    type="number"
                    value={exitFees}
                    onChange={(e) => setExitFees(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pr-3 py-2 rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                    style={{
                      paddingLeft: getTokenPadding(roiCurrency),
                    }}
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
                          formatCurrency(0, roiCurrency)
                        ) : calculationResult.isProfit ? (
                          <>
                            <ArrowUp size={26} className="inline mr-2" />
                            {formatCurrency(
                              Math.abs(calculationResult.absoluteProfit),
                              roiCurrency
                            )}
                          </>
                        ) : (
                          <>
                            <ArrowDown size={26} className="inline mr-2" />
                            {formatCurrency(
                              Math.abs(calculationResult.absoluteProfit),
                              roiCurrency
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
                      {formatCurrency(
                        calculationResult.totalInvestment,
                        roiCurrency
                      )}
                    </div>
                  </div>

                  {/* Total Exit Amount */}
                  <div className="py-3">
                    <div className="text-base text-gray-500 mb-1">
                      Total Exit Amount
                    </div>
                    <div className="text-xl font-bold text-gray-600">
                      {formatCurrency(calculationResult.netReturn, roiCurrency)}
                    </div>
                  </div>

                  {/* Total Fees */}
                  <div className="py-3 last:pb-2">
                    <div className="text-base text-gray-500 mb-1">
                      Total Fees
                    </div>
                    <div className="text-xl font-bold text-gray-600">
                      {formatCurrency(calculationResult.totalFees, roiCurrency)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4 mx-auto">
          {/* Staking Calculator */}
          <div className="col-span-3 bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
            <div className="bg-teal-700 text-white p-4 font-medium flex items-center justify-between">
              <div className="flex items-center">
                <BarChart2 size={20} className="mr-2" />
                <span>Staking Calculator</span>
              </div>
              <button
                onClick={clearStakingInputs}
                className="px-3 py-1 text-sm bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
              >
                Clear All
              </button>
            </div>
            <div className="p-5">
              <div className="grid grid-cols-9 gap-4">
                {/* Token Selection */}
                <div className="col-span-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                    Token
                  </label>
                  <select
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    className="w-full rounded-lg border-r-8 border-transparent outline outline-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                  >
                    {coins.map((t) => (
                      <option key={t.symbol} value={t.symbol}>
                        {t.name} ({t.symbol})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Staking Rate */}
                <div className="col-span-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                    Staking Rate
                  </label>
                  <div className="relative shadow-sm">
                    <input
                      type="text"
                      inputMode="decimal"
                      value={stakingRate ? `${stakingRate}%` : ""}
                      onChange={(e) => {
                        const value = e.target.value.replace(/[^0-9.]/g, "");
                        if (
                          value === "" ||
                          (!isNaN(value) && !isNaN(parseFloat(value)))
                        ) {
                          setStakingRate(value);
                          requestAnimationFrame(() => {
                            e.target.setSelectionRange(
                              value.length,
                              value.length
                            );
                          });
                        }
                      }}
                      onKeyDown={(e) => {
                        if (e.key === "Backspace" && stakingRate.length > 0) {
                          const newValue = stakingRate.slice(0, -1);
                          setStakingRate(newValue);
                          e.preventDefault();
                        }
                      }}
                      onFocus={(e) => {
                        e.target.placeholder = "";
                        const valueLength = stakingRate.length;
                        e.target.setSelectionRange(valueLength, valueLength);
                      }}
                      onBlur={(e) => (e.target.placeholder = "0.00%")}
                      placeholder="0.00%"
                      className="block w-full pl-3 pr-16 py-[0.4375rem] rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                    />
                    <select
                      value={isAPR ? "APR" : "APY"}
                      onChange={(e) => setIsAPR(e.target.value === "APR")}
                      className="absolute inset-y-0 right-0 w-16 rounded-r-lg bg-gray-200 border-r-3 border-b-2 outline outline-gray-300 border-transparent text-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent text-center"
                    >
                      <option value="APR">APR</option>
                      <option value="APY">APY</option>
                    </select>
                  </div>
                </div>

                {/* Compounding Frequency */}
                <div className="col-span-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                    Compounding Frequency
                  </label>
                  <select
                    value={compoundingFrequency}
                    onChange={(e) => setCompoundingFrequency(e.target.value)}
                    className="w-full rounded-lg border-r-8 border-transparent outline outline-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>

                {/* Currency Selection */}
                <div className="col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                    Currency
                  </label>
                  <select
                    value={stakingCurrency}
                    onChange={(e) => setStakingCurrency(e.target.value)}
                    className="w-full rounded-lg border-r-8 border-transparent outline outline-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent shadow-sm"
                  >
                    {currencies.map((curr) => (
                      <option key={curr} value={curr}>
                        {curr}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Initial Investment */}
                <div className="col-span-2">
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-sm font-medium text-gray-700 pl-1">
                      Initial Investment
                    </label>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">
                        {stakingCurrency}
                      </span>
                      <div
                        className="relative w-8 h-4 rounded-full bg-gray-200 cursor-pointer"
                        onClick={() => setIsTokenAmount(!isTokenAmount)}
                      >
                        <div
                          className={`absolute top-0.5 h-3 w-3 rounded-full bg-teal-600 transform transition-transform ease-in-out duration-300 ${
                            isTokenAmount ? "translate-x-4" : "translate-x-0.5"
                          }`}
                        />
                      </div>
                      <span className="text-sm text-gray-600">{token}</span>
                    </div>
                  </div>
                  <div className="relative shadow-sm">
                    <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                      <span
                        className={`bg-gray-200 text-gray-600 h-full flex items-center rounded-l-lg border-r border-gray-300 ${
                          isTokenAmount ? "px-2 py-2" : "px-3 py-2"
                        }`}
                      >
                        {isTokenAmount
                          ? token
                          : getCurrencySymbol(stakingCurrency)}
                      </span>
                    </div>
                    <input
                      type="number"
                      value={stakingAmount}
                      onChange={(e) => setStakingAmount(e.target.value)}
                      placeholder="0.00"
                      className={`block w-full pr-3 py-[0.4375rem] rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent`}
                      style={{
                        paddingLeft: isTokenAmount
                          ? getTokenPadding(token, true)
                          : getTokenPadding(stakingCurrency),
                      }}
                    />
                  </div>
                </div>

                {/* Staking Duration */}
                <div className="col-span-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1 pl-1">
                    Staking Duration
                  </label>
                  <div className="relative shadow-sm">
                    <input
                      type="number"
                      value={stakingDuration}
                      onChange={(e) => setStakingDuration(e.target.value)}
                      placeholder="0"
                      className="block w-full px-3 py-[0.4375rem] rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                    />
                    <select
                      value={durationUnit}
                      onChange={(e) => setDurationUnit(e.target.value)}
                      className="absolute inset-y-0 right-0 w-20 rounded-r-lg bg-gray-200 border-r-3 border-b-2 border-transparent outline outline-gray-300 text-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent text-center"
                    >
                      <option value="days">Days</option>
                      <option value="months">Months</option>
                      <option value="years">Years</option>
                    </select>
                  </div>
                </div>

                {/* Token Price */}
                <div className="col-span-3">
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
                  <div className="relative shadow-sm">
                    <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none">
                      <span className="bg-gray-200 text-gray-600 px-3 py-2 h-full flex items-center rounded-l-lg border-r border-gray-300">
                        {getCurrencySymbol(stakingCurrency)}
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
                      className={`block w-full pr-3 py-[0.4375rem] rounded-lg outline outline-gray-300 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent ${
                        useCurrentPrice ? "bg-gray-100" : ""
                      }`}
                      style={{
                        paddingLeft: getTokenPadding(stakingCurrency),
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Investment Chart */}
          <div className="col-span-2 bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
            <div className="bg-teal-700 text-white p-4 font-medium flex items-center">
              <BarChart2 size={20} className="mr-2" />
              <span>Investment Growth</span>
            </div>
            <div className="px-3 pt-4">
              {/* Total Rewards Summary */}
              <div className="mb-3 text-center">
                <div className="text-lg text-gray-500 mb-1">
                  Total Rewards in {stakingDuration || "0"} {durationUnit}
                </div>
                <div
                  className={`text-3xl font-bold mb-1 ${
                    stakingResults.total.fiat === 0
                      ? "text-gray-600"
                      : "text-green-600"
                  }`}
                >
                  {formatCurrency(stakingResults.total.fiat, stakingCurrency)}
                </div>
                <div className="text-base text-gray-500">
                  {stakingResults.total.tokens === 0
                    ? "0"
                    : stakingResults.total.tokens.toFixed(8)}{" "}
                  {token}
                </div>
              </div>

              <div className="h-[300px]">
                <Line
                  data={generateChartData()}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      x: {
                        grid: {
                          display: false,
                        },
                        title: {
                          display: true,
                          text: "Time",
                          font: {
                            size: 14,
                            weight: "bold",
                          },
                          padding: {
                            top: 5,
                          },
                        },
                      },
                      y: {
                        beginAtZero: false,
                        grid: {
                          display: false,
                        },
                        title: {
                          display: true,
                          text: `Total Value (${stakingCurrency})`,
                          font: {
                            size: 14,
                            weight: "bold",
                          },
                          padding: {
                            bottom: 5,
                          },
                        },
                        min: function () {
                          const currentMarketPrice = coins.find(
                            (t) => t.symbol === token
                          ).price;
                          const displayPrice = useCurrentPrice
                            ? currentMarketPrice
                            : parseFloat(customTokenPrice) || 0;
                          const inputAmount = parseFloat(stakingAmount);
                          const principal = isTokenAmount
                            ? inputAmount
                            : inputAmount / currentMarketPrice;
                          return principal * displayPrice;
                        },
                        ticks: {
                          callback: function (value) {
                            return formatCurrency(value, stakingCurrency);
                          },
                        },
                      },
                    },
                    plugins: {
                      legend: {
                        display: false,
                      },
                      tooltip: {
                        mode: "index",
                        displayColors: false,
                        intersect: false,
                        callbacks: {
                          label: function (context) {
                            return `${formatCurrency(
                              context.parsed.y,
                              stakingCurrency
                            )}`;
                          },
                        },
                      },
                    },
                  }}
                />
              </div>
            </div>
          </div>

          {/* Staking Returns */}
          <div className="col-span-1 bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
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
                    {formatCurrency(stakingResults.daily.fiat, stakingCurrency)}
                  </div>
                  <div className="text-base text-gray-500">
                    {stakingResults.daily.tokens === 0
                      ? "0"
                      : stakingResults.daily.tokens.toFixed(8)}{" "}
                    {token}
                  </div>
                </div>

                {/* Monthly Staking Returns */}
                <div className="py-5">
                  <div className="text-lg text-gray-500 mb-2">
                    Monthly Staking Returns
                  </div>
                  <div className="text-3xl font-bold text-gray-600 mb-1">
                    {formatCurrency(
                      stakingResults.monthly.fiat,
                      stakingCurrency
                    )}
                  </div>
                  <div className="text-base text-gray-500">
                    {stakingResults.monthly.tokens === 0
                      ? "0"
                      : stakingResults.monthly.tokens.toFixed(8)}{" "}
                    {token}
                  </div>
                </div>

                {/* Yearly Staking Returns */}
                <div className="py-5 last:pb-2">
                  <div className="text-lg text-gray-500 mb-2">
                    Yearly Staking Returns
                  </div>
                  <div className="text-3xl font-bold text-gray-600 mb-1">
                    {formatCurrency(
                      stakingResults.yearly.fiat,
                      stakingCurrency
                    )}
                  </div>
                  <div className="text-base text-gray-500">
                    {stakingResults.yearly.tokens === 0
                      ? "0"
                      : stakingResults.yearly.tokens.toFixed(8)}{" "}
                    {token}
                  </div>
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
