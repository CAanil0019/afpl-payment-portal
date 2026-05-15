import { BrowserRouter, Routes, Route } from "react-router-dom";
import CustomerPayment from "./pages/CustomerPayment";
import AdminLogin from "./pages/AdminLogin";
import AdminReport from "./pages/AdminReport";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CustomerPayment />} />
        <Route path="/admin-login" element={<AdminLogin />} />
        <Route path="/admin-report" element={<AdminReport />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;