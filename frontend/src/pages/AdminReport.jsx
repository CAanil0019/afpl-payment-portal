import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const API_BASE = "http://127.0.0.1:8000";

function AdminReport() {
  const [transactions, setTransactions] = useState([]);
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("admin_token");

    if (!token) {
      navigate("/admin-login");
      return;
    }

    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      const token = localStorage.getItem("admin_token");

      const res = await axios.get(`${API_BASE}/reports/transactions`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setTransactions(res.data);
    } catch (error) {
      console.error(error);
      alert("Unable to load transactions");
    }
  };

  const logout = () => {
    localStorage.removeItem("admin_token");
    navigate("/admin-login");
  };

  const filteredTransactions = transactions.filter((txn) => {
    const txnDate = txn.transaction_date?.slice(0, 10);

    if (fromDate && txnDate < fromDate) return false;
    if (toDate && txnDate > toDate) return false;

    return true;
  });

  const downloadCSV = async () => {
  try {
    const token = localStorage.getItem("admin_token");

    const res = await axios.get(`${API_BASE}/reports/transactions-csv`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([res.data]));

    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "transaction_report.csv");
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error(error);
    alert("CSV download failed");
  }
};

  return (
    <div className="container mt-4 mb-5">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4>Admin Transaction Report</h4>

        <button className="btn btn-danger" onClick={logout}>
          Logout
        </button>
      </div>

      <div className="card shadow mb-3">
        <div className="card-body">
          <div className="row">
            <div className="col-md-3">
              <label>From Date</label>
              <input
                type="date"
                className="form-control"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
              />
            </div>

            <div className="col-md-3">
              <label>To Date</label>
              <input
                type="date"
                className="form-control"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
              />
            </div>

            <div className="col-md-6 d-flex align-items-end">
              <button className="btn btn-secondary me-2" onClick={loadTransactions}>
                Refresh Report
              </button>

              <button className="btn btn-success" onClick={downloadCSV}>
                Download CSV
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="card shadow">
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-bordered table-striped">
              <thead>
                <tr>
                  <th>Ref No</th>
                  <th>Customer</th>
                  <th>Loan No</th>
                  <th>Mobile</th>
                  <th>Charge</th>
                  <th>Amount</th>
                  <th>Gateway</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>

              <tbody>
                {filteredTransactions.map((txn) => (
                  <tr key={txn.transaction_id}>
                    <td>{txn.order_reference}</td>
                    <td>{txn.customer_name}</td>
                    <td>{txn.loan_account_number}</td>
                    <td>{txn.mobile_number}</td>
                    <td>{txn.charge_type}</td>
                    <td>₹{Number(txn.total_amount).toFixed(2)}</td>
                    <td>{txn.gateway_name}</td>
                    <td>{txn.payment_status}</td>
                    <td>{txn.transaction_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredTransactions.length === 0 && (
            <div className="alert alert-info">No transactions found.</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdminReport;