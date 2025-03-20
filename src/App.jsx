import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Cryptocurrencies from "./pages/Cryptocurrencies";
import Compare from "./pages/Compare";
import Calculators from "./pages/Calculators";
import Learn from "./pages/Learn";
import Portfolio from "./pages/Portfolio";
import Watchlist from "./pages/Watchlist";
import Navbar from "./components/Navbar";
import Converter from "./pages/Converter";

import BnbCoins from "./pages/categories/BnbCoins";
import SolCoins from "./pages/categories/SolCoins";
import DotCoins from "./pages/categories/DotCoins";
import SmartContractCoins from "./pages/categories/SmartContractCoins";
import LayerOneCoins from "./pages/categories/LayerOneCoins";
import LayerTwoCoins from "./pages/categories/LayerTwoCoins";
import DefiCoins from "./pages/categories/DefiCoins";
import AiCoins from "./pages/categories/AiCoins";
import GamingCoins from "./pages/categories/GamingCoins";
import InfrastructureCoins from "./pages/categories/InfrastructureCoins";
import RwaCoins from "./pages/categories/RwaCoins";
import MemeCoins from "./pages/categories/MemeCoins";
import NftCoins from "./pages/categories/NftCoins";

const App = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        {/* Navbar Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/cryptocurrencies" element={<Cryptocurrencies />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/converter" element={<Converter />} />
        <Route path="/calculators" element={<Calculators />} />
        <Route path="/calculators/roi" element={<Calculators />} />
        <Route path="/calculators/staking" element={<Calculators />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/watchlist" element={<Watchlist />} />

        {/* Category Routes */}
        <Route path="/category/bnb" element={<BnbCoins />} />
        <Route path="/category/sol" element={<SolCoins />} />
        <Route path="/category/dot" element={<DotCoins />} />
        <Route
          path="/category/smart-contract"
          element={<SmartContractCoins />}
        />
        <Route path="/category/layer-1" element={<LayerOneCoins />} />
        <Route path="/category/layer-2" element={<LayerTwoCoins />} />
        <Route path="/category/defi" element={<DefiCoins />} />
        <Route path="/category/ai" element={<AiCoins />} />
        <Route path="/category/gaming" element={<GamingCoins />} />
        <Route
          path="/category/infrastructure"
          element={<InfrastructureCoins />}
        />
        <Route path="/category/rwa" element={<RwaCoins />} />
        <Route path="/category/meme" element={<MemeCoins />} />
        <Route path="/category/nft" element={<NftCoins />} />
      </Routes>
    </Router>
  );
};

export default App;
