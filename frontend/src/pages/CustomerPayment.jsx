import { useEffect, useState } from "react";
import axios from "axios";
import "./CustomerPayment.css";
import logo from "../assets/ANNAPURNA.png";

const API_BASE = "http://127.0.0.1:8000";

function CustomerPayment() {
  const [charges, setCharges] = useState([]);

  const [form, setForm] = useState({
    customer_name: "",
    loan_account_number: "",
    mobile_number: "",
    charge_id: "",
    gateway_name: "RAZORPAY",
  });

  const [selectedCharge, setSelectedCharge] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [timeLeft, setTimeLeft] = useState(300);

  useEffect(() => {
    axios
      .get(`${API_BASE}/charges/`)
      .then((res) => setCharges(res.data))
      .catch((err) => console.error(err));
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          alert("Session expired");
          window.location.reload();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm({ ...form, [name]: value });

    if (name === "charge_id") {
      const charge = charges.find((c) => c.charge_id === Number(value));
      setSelectedCharge(charge || null);
    }
  };

  const calculateTotal = () => {
    if (!selectedCharge) return null;

    const base = Number(selectedCharge.base_amount);
    const gst = (base * Number(selectedCharge.gst_percent)) / 100;
    const total = base + gst;

    return { base, gst, total };
  };

  const validateForm = () => {
    if (
      !form.customer_name ||
      !form.loan_account_number ||
      !form.mobile_number ||
      !form.charge_id
    ) {
      alert("Please fill all fields");
      return false;
    }

    if (!/^[6-9][0-9]{9}$/.test(form.mobile_number)) {
      alert("Please enter valid mobile number");
      return false;
    }

    return true;
  };

  const payWithCCAvenue = async () => {
    try {
      const res = await axios.post(`${API_BASE}/payment/create-ccavenue-order`, {
        ...form,
        charge_id: Number(form.charge_id),
        gateway_name: "CCAVENUE",
      });

      const data = res.data;

      const formElement = document.createElement("form");
      formElement.method = "POST";
      formElement.action = data.gateway_url;

      const encInput = document.createElement("input");
      encInput.type = "hidden";
      encInput.name = "encRequest";
      encInput.value = data.enc_request;

      const accessInput = document.createElement("input");
      accessInput.type = "hidden";
      accessInput.name = "access_code";
      accessInput.value = data.access_code;

      formElement.appendChild(encInput);
      formElement.appendChild(accessInput);
      document.body.appendChild(formElement);
      formElement.submit();
    } catch (error) {
      console.error(error);
      alert("CCAvenue order creation failed");
    }
  };

  const payWithRazorpay = async () => {
    try {
      const res = await axios.post(`${API_BASE}/payment/create-transaction`, {
        ...form,
        charge_id: Number(form.charge_id),
      });

      const data = res.data;

      const options = {
        key: data.key,
        amount: Number(data.amount) * 100,
        currency: data.currency,
        name: "Annapurna Finance Pvt. Ltd.",
        description: "Customer Service Request Payment",
        order_id: data.razorpay_order_id,

        handler: async function (response) {
          try {
            const verifyRes = await axios.post(
              `${API_BASE}/payment/verify-payment`,
              {
                order_reference: data.order_reference,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              }
            );

            setPaymentStatus({
              success: true,
              order_reference: verifyRes.data.order_reference,
              payment_id: response.razorpay_payment_id,
            });
          } catch (error) {
            console.error(error);
            setPaymentStatus({
              success: false,
              error: "Payment verification failed",
            });
          }
        },

        prefill: {
          name: form.customer_name,
          contact: form.mobile_number,
        },

        theme: {
          color: "#003b73",
        },
      };

      const razorpay = new window.Razorpay(options);

      razorpay.on("payment.failed", function (response) {
        setPaymentStatus({
          success: false,
          error: response.error.description,
        });
      });

      razorpay.open();
    } catch (error) {
      console.error(error);
      alert("Payment order creation failed");
    }
  };

  const payNow = async () => {
    if (!validateForm()) return;

    if (form.gateway_name === "CCAVENUE") {
      await payWithCCAvenue();
      return;
    }

    await payWithRazorpay();
  };

  const downloadReceipt = () => {
    if (!paymentStatus?.order_reference) {
      alert("Receipt reference not found");
      return;
    }

    window.open(
      `${API_BASE}/payment/download-receipt/${paymentStatus.order_reference}`,
      "_blank"
    );
  };

  const amount = calculateTotal();

  return (
    <div className="payment-bg">
      <div className="container">
        <div className="card shadow payment-card">
          <div className="afpl-header">
            <div className="d-flex align-items-center justify-content-between">
              <img src={logo} alt="Annapurna Finance" style={{ height: "70px" }} />

              <div className="text-end">
                <h3 className="afpl-title">Customer Service Request Payment Portal</h3>
                <p className="afpl-subtitle">Secure Online Payment</p>
              </div>
            </div>
          </div>

          <div className="card-body p-4">
            <div className="alert alert-warning mb-4">
              Session expires in: {Math.floor(timeLeft / 60)}:
              {(timeLeft % 60).toString().padStart(2, "0")}
            </div>

            <div className="section-title">
              <span className="step-badge">1</span>
              Customer Details
            </div>

            <div className="row g-3">
              <div className="col-md-4">
                <label className="form-label">Customer Name</label>
                <input
                  type="text"
                  name="customer_name"
                  className="form-control"
                  value={form.customer_name}
                  onChange={handleChange}
                  placeholder="Enter customer name"
                />
              </div>

              <div className="col-md-4">
                <label className="form-label">Loan Account Number</label>
                <input
                  type="text"
                  name="loan_account_number"
                  className="form-control"
                  value={form.loan_account_number}
                  onChange={handleChange}
                  placeholder="Enter loan account number"
                />
              </div>

              <div className="col-md-4">
                <label className="form-label">Registered Mobile Number</label>
                <input
                  type="text"
                  name="mobile_number"
                  maxLength="10"
                  className="form-control"
                  value={form.mobile_number}
                  onChange={handleChange}
                  placeholder="10 digit mobile number"
                />
              </div>
            </div>

            <hr className="my-4" />

            <div className="section-title">
              <span className="step-badge">2</span>
              Charge Selection
            </div>

            <div className="row g-3">
              <div className="col-md-6">
                <label className="form-label">Charge Type</label>
                <select
                  name="charge_id"
                  className="form-select"
                  value={form.charge_id}
                  onChange={handleChange}
                >
                  <option value="">Select Charge Type</option>
                  {charges.map((charge) => (
                    <option key={charge.charge_id} value={charge.charge_id}>
                      {charge.charge_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="col-md-6">
                <label className="form-label">Payment Gateway</label>
                <select
                  name="gateway_name"
                  className="form-select"
                  value={form.gateway_name}
                  onChange={handleChange}
                >
                  <option value="RAZORPAY">Razorpay</option>
                  <option value="CCAVENUE">CCAvenue</option>
                </select>
              </div>
            </div>

            {selectedCharge && amount && (
              <div className="amount-box mt-4">
                <h6 className="fw-bold">{selectedCharge.charge_name}</h6>
                <p className="text-muted mb-3">{selectedCharge.description}</p>

                <table className="table table-bordered bg-white mb-0">
                  <tbody>
                    <tr>
                      <td>Base Amount</td>
                      <td className="text-end">₹{amount.base.toFixed(2)}</td>
                    </tr>

                    <tr>
                      <td>GST @ {selectedCharge.gst_percent}%</td>
                      <td className="text-end">₹{amount.gst.toFixed(2)}</td>
                    </tr>

                    <tr className="total-row">
                      <th>Total Payable</th>
                      <th className="text-end">₹{amount.total.toFixed(2)}</th>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            <hr className="my-4" />

            <div className="section-title">
              <span className="step-badge">3</span>
              Payment Confirmation
            </div>

            <button className="btn btn-success pay-btn" onClick={payNow}>
              Proceed to Payment
            </button>

            {paymentStatus && (
              <div
                className={`alert mt-4 ${
                  paymentStatus.success
                    ? "alert-success success-box"
                    : "alert-danger failure-box"
                }`}
              >
                {paymentStatus.success ? (
                  <>
                    <h4>Payment Successful</h4>
                    <p>Your payment has been received successfully.</p>

                    <p>
                      <strong>Reference Number:</strong>{" "}
                      {paymentStatus.order_reference}
                    </p>

                    <p>
                      <strong>Payment ID:</strong> {paymentStatus.payment_id}
                    </p>

                    <button
                      className="btn btn-primary mt-2"
                      onClick={downloadReceipt}
                    >
                      Download Receipt
                    </button>
                  </>
                ) : (
                  <>
                    <h4>Payment Failed</h4>
                    <p>
                      {paymentStatus.error ||
                        "Transaction could not be completed"}
                    </p>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CustomerPayment;