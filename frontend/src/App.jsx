import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Home from './pages/Home';
import Navbar from './components/Navbar';
import Profile from "./pages/Profile";


function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        {/* thêm các route khác sau */}
      </Routes>
    </Router>
  );
}

export default App;
