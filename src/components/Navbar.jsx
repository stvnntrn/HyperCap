import { Link } from "react-router-dom";
import { FaSearch, FaBriefcase, FaStar } from "react-icons/fa"; // Import icons

const Navbar = () => {
  return (
    <nav className="bg-white text-gray-900 py-4 w-full border-b border-[#EFF2F5]">
      <div className="container mx-auto flex justify-between items-center px-6">
        <div className="flex items-center space-x-8">
          <Link
            to="/"
            className="text-2xl font-bold hover:text-gray-600 mb-1.5"
          >
            HyperCap
          </Link>
          <ul className="flex space-x-8 font-semibold">
            <li>
              <Link to="/compare" className="hover:text-gray-600">
                Compare
              </Link>
            </li>
            <li>
              <Link to="/roi-calculator" className="hover:text-gray-600">
                ROI Calculator
              </Link>
            </li>
            <li>
              <Link to="/staking-calculator" className="hover:text-gray-600">
                Staking Calculator
              </Link>
            </li>
            <li>
              <Link to="/learn" className="hover:text-gray-600">
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
                className="flex items-center space-x-2 hover:text-gray-600"
              >
                <FaBriefcase className="text-gray-600" />
                <span>Portfolio</span>
              </Link>
            </li>
            <li>
              <Link
                to="/watchlist"
                className="flex items-center space-x-2 hover:text-gray-600"
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
              className="bg-gray-200 text-gray-900 pl-10 pr-3 py-1.5 rounded-md w-44 text-sm focus:outline-none focus:ring-2 focus:ring-gray-500"
            />
            <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-600" />
          </div>

          <button className="bg-blue-600 text-white px-4 py-1.5 rounded-md text-sm font-semibold hover:bg-blue-500">
            Log In
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
