import { Link } from "react-router-dom";
import { FaSearch, FaBriefcase, FaStar } from "react-icons/fa";
import { Calculator, TrendingUp } from "lucide-react";

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
            <li>
              <Link to="/cryptocurrencies" className="hover:text-primary">
                Cryptocurrencies
              </Link>
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
              <ul className="absolute left-0 mt-2 bg-white shadow-lg rounded-md w-56 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
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
