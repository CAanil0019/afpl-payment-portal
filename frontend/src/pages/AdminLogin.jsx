import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

function AdminLogin() {
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const login = async () => {
    try {
      const res = await axios.post(`${API_BASE}/auth/admin-login`, {
        username: user,
        password: password,
      });

      localStorage.setItem("admin_token", res.data.access_token);
      navigate("/admin-report");
    } catch (error) {
      alert("Invalid login");
    }
  };

  return (
    <div className="container mt-5">
      <div className="card shadow mx-auto" style={{ maxWidth: "400px" }}>
        <div className="card-header bg-dark text-white">
          <h5 className="mb-0">Admin Login</h5>
        </div>

        <div className="card-body">
          <label>User ID</label>
          <input className="form-control mb-3" value={user} onChange={(e) => setUser(e.target.value)} />

          <label>Password</label>
          <input type="password" className="form-control mb-3" value={password} onChange={(e) => setPassword(e.target.value)} />

          <button className="btn btn-primary w-100" onClick={login}>
            Login
          </button>
        </div>
      </div>
    </div>
  );
}

export default AdminLogin;