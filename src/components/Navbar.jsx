import { Link } from "react-router-dom";
import { FaSearch, FaBriefcase, FaStar } from "react-icons/fa";
import {
  Calculator,
  TrendingUp,
  Blocks,
  Brain,
  Wallet,
  Gamepad2,
  Building2,
  Rocket,
  Gem,
  Globe,
  Zap,
  Link2,
  Boxes,
  Coins,
  ChevronRight,
} from "lucide-react";

const Navbar = () => {
  return (
    <nav className="bg-white text-gray-900 py-4 w-full border-b border-[#EFF2F5]">
      <div className="container mx-auto flex justify-between items-center px-6">
        <div className="flex items-center space-x-7">
          <Link
            to="/"
            className="text-3xl font-bold hover:text-primary mb-1 font-nunito"
          >
            HyperCap
          </Link>
          <ul className="flex space-x-7 font-semibold">
            <li className="relative group">
              <Link
                to="/"
                className="hover:text-primary flex items-center space-x-1"
              >
                <span>Cryptocurrencies</span>
              </Link>
              <ul className="absolute left-0 mt-2 bg-white shadow-lg rounded-md w-56 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <li className="relative group/inner">
                  <div className="flex items-center justify-between px-4 py-2 hover:bg-gray-100 cursor-pointer">
                    <span className="flex items-center">
                      <Blocks className="w-4 h-4 mr-2" /> Categories
                    </span>
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  </div>
                  <ul className="absolute left-full top-0 bg-white shadow-lg rounded-md w-56 opacity-0 invisible group-hover/inner:opacity-100 group-hover/inner:visible transition-all duration-200">
                    <li>
                      <Link
                        to="/category/bnb"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Coins className="w-4 h-4 mr-2" /> BNB
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/sol"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Zap className="w-4 h-4 mr-2" /> SOL
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/dot"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Globe className="w-4 h-4 mr-2" /> DOT
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/smart-contract"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Blocks className="w-4 h-4 mr-2" /> Smart Contract
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/layer-1"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Blocks className="w-4 h-4 mr-2" /> Layer 1
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/layer-2"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Boxes className="w-4 h-4 mr-2" /> Layer 2
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/defi"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Wallet className="w-4 h-4 mr-2" /> DeFi
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/ai"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Brain className="w-4 h-4 mr-2" /> AI
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/gaming"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Gamepad2 className="w-4 h-4 mr-2" /> Gaming
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/infrastructure"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Link2 className="w-4 h-4 mr-2" /> Infrastructure
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/rwa"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Building2 className="w-4 h-4 mr-2" /> RWA
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/meme"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Rocket className="w-4 h-4 mr-2" /> Meme
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/category/nft"
                        className="flex items-center px-4 py-2 hover:bg-gray-100"
                      >
                        <Gem className="w-4 h-4 mr-2" /> NFT
                      </Link>
                    </li>
                  </ul>
                </li>
              </ul>
            </li>
            <li>
              <Link to="/compare" className="hover:text-primary">
                Compare
              </Link>
            </li>
            <li className="relative group">
              <Link
                to="/calculators"
                className="flex items-center space-x-1 hover:text-primary focus:outline-none"
              >
                Calculators
              </Link>
              <ul className="absolute left-0 mt-2 bg-white shadow-lg rounded-md w-56 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <li>
                  <Link
                    to="/calculators"
                    className="flex items-center px-4 py-2 hover:bg-gray-100"
                  >
                    <Calculator className="w-4 h-4 mr-2" /> ROI Calculator
                  </Link>
                </li>
                <li>
                  <Link
                    to="/calculators"
                    className="flex items-center px-4 py-2 hover:bg-gray-100"
                  >
                    <TrendingUp className="w-4 h-4 mr-2" /> Staking Calculator
                  </Link>
                </li>
              </ul>
            </li>
            <li>
              <Link to="/learn" className="hover:text-primary">
                Learn
              </Link>
            </li>
          </ul>
        </div>

        <div className="flex items-center space-x-6">
          <ul className="flex space-x-6 font-semibold">
            <li>
              <Link
                to="/portfolio"
                className="flex items-center space-x-2 hover:text-primary"
              >
                <FaBriefcase className="text-[#88501c]" />
                <span>Portfolio</span>
              </Link>
            </li>
            <li>
              <Link
                to="/watchlist"
                className="flex items-center space-x-2 hover:text-primary"
              >
                <FaStar className="text-yellow-500" />
                <span>Watchlist</span>
              </Link>
            </li>
          </ul>

          <div className="relative">
            <input
              type="text"
              placeholder="Search..."
              className="bg-gray-200 text-gray-900 pl-10 pr-3 py-1.5 rounded-md w-44 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-600" />
          </div>

          <button className="bg-primary hover:bg-primary text-white px-4 py-1.5 rounded-md text-sm font-semibold cursor-pointer transition-all duration-300 ease-in-out transform hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary">
            Log In
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
