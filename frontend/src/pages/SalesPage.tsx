import { useEffect, useState } from "react";
import { api, Sale, Product } from "../api/client";

const PAYMENT_METHODS = ["CASH", "CREDIT_CARD", "DEBIT_CARD", "ONLINE"];

interface LineItem {
  product_id: string;
  quantity: string;
}

export default function SalesPage() {
  const [sales, setSales] = useState<Sale[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState("");
  const [customer, setCustomer] = useState("");
  const [payment, setPayment] = useState("CASH");
  const [items, setItems] = useState<LineItem[]>([{ product_id: "", quantity: "1" }]);

  const load = () => api.sales.list().then(setSales);

  useEffect(() => {
    load();
    api.products.list().then(setProducts);
  }, []);

  const addLine = () => setItems([...items, { product_id: "", quantity: "1" }]);

  const updateLine = (idx: number, field: keyof LineItem, value: string) => {
    const updated = [...items];
    updated[idx] = { ...updated[idx], [field]: value };
    setItems(updated);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await api.sales.create({
        customer_name: customer || undefined,
        payment_method: payment,
        items: items.map((i) => ({
          product_id: parseInt(i.product_id),
          quantity: parseInt(i.quantity),
        })),
      });
      setShowModal(false);
      setCustomer("");
      setItems([{ product_id: "", quantity: "1" }]);
      load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create sale");
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Sales</h2>
        <p>Create transactions and view sales history</p>
      </div>

      <div className="toolbar">
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ New Sale</button>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Customer</th><th>Date</th><th>Payment</th><th>Items</th><th>Total</th>
            </tr>
          </thead>
          <tbody>
            {sales.map((s) => (
              <tr key={s.sale_id}>
                <td>#{s.sale_id}</td>
                <td>{s.customer_name || "Walk-in"}</td>
                <td>{new Date(s.sale_timestamp).toLocaleString()}</td>
                <td><span className="badge badge-green">{s.payment_method}</span></td>
                <td>{s.items.length} item(s)</td>
                <td><strong>${Number(s.total_amount).toFixed(2)}</strong></td>
              </tr>
            ))}
            {sales.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: "center", color: "#94a3b8" }}>No sales yet</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 600 }}>
            <h3>Create Sale</h3>
            {error && <div className="error-msg">{error}</div>}
            <form onSubmit={handleCreate}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Customer Name (optional)</label>
                  <input className="input" value={customer} onChange={(e) => setCustomer(e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Payment Method</label>
                  <select className="select" value={payment} onChange={(e) => setPayment(e.target.value)}>
                    {PAYMENT_METHODS.map((m) => <option key={m} value={m}>{m}</option>)}
                  </select>
                </div>
              </div>

              <h4 style={{ margin: "16px 0 8px", fontSize: "0.9rem" }}>Line Items</h4>
              {items.map((item, idx) => (
                <div key={idx} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
                  <select className="select" required style={{ flex: 2 }} value={item.product_id}
                    onChange={(e) => updateLine(idx, "product_id", e.target.value)}>
                    <option value="">Select product</option>
                    {products.map((p) => (
                      <option key={p.product_id} value={p.product_id}>
                        {p.sku} — {p.name} (${Number(p.unit_price).toFixed(2)})
                      </option>
                    ))}
                  </select>
                  <input className="input" type="number" min="1" required style={{ width: 80 }}
                    value={item.quantity} onChange={(e) => updateLine(idx, "quantity", e.target.value)} />
                </div>
              ))}
              <button type="button" className="btn btn-secondary" onClick={addLine} style={{ marginBottom: 12 }}>
                + Add Line Item
              </button>

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Complete Sale</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
