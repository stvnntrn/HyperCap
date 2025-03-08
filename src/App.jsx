import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Cryptocurrencies from "./pages/Cryptocurrencies";
import Compare from "./pages/Compare";
import Calculators from "./pages/Calculators";
import ROICalculator from "./pages/ROICalculator";
import StakingCalculator from "./pages/StakingCalculator";
import Learn from "./pages/Learn";
import Portfolio from "./pages/Portfolio";
import Watchlist from "./pages/Watchlist";
import Navbar from "./components/Navbar";

const App = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/cryptocurrencies" element={<Cryptocurrencies />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/calculators" element={<Calculators />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/watchlist" element={<Watchlist />} />
      </Routes>
    </Router>
  );
};

export default App;
