import { useEffect, useState } from "react";
import { api, InventoryItem } from "../api/client";

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [adjustId, setAdjustId] = useState<number | null>(null);
  const [newQty, setNewQty] = useState("");
  const [stockInId, setStockInId] = useState<number | null>(null);
  const [stockInQty, setStockInQty] = useState("");
  const [error, setError] = useState("");

  const load = () => api.inventory.list().then(setItems);

  useEffect(() => { load(); }, []);

  const handleStockIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stockInId) return;
    setError("");
    try {
      await api.inventory.stockIn(stockInId, parseInt(stockInQty), "Manual stock-in");
      setStockInId(null);
      setStockInQty("");
      load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed");
    }
  };

  const handleAdjust = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!adjustId) return;
    setError("");
    try {
      await api.inventory.adjust(adjustId, parseInt(newQty), "Manual adjustment");
      setAdjustId(null);
      setNewQty("");
      load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed");
    }
  };

  const stockStatus = (item: InventoryItem) => {
    const level = item.reorder_level ?? 0;
    if (item.quantity_available <= level) return "badge-red";
    if (item.quantity_available <= level * 2) return "badge-yellow";
    return "badge-green";
  };

  return (
    <div>
      <div className="page-header">
        <h2>Inventory</h2>
        <p>Current stock levels, adjustments, and low-stock alerts</p>
      </div>

      {error && <div className="error-msg">{error}</div>}

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>SKU</th><th>Product</th><th>Qty Available</th>
              <th>Reorder Level</th><th>Status</th><th>Last Updated</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.inventory_id}>
                <td><code>{item.sku}</code></td>
                <td>{item.product_name}</td>
                <td><strong>{item.quantity_available}</strong></td>
                <td>{item.reorder_level}</td>
                <td>
                  <span className={`badge ${stockStatus(item)}`}>
                    {item.quantity_available <= (item.reorder_level ?? 0) ? "Low" : "OK"}
                  </span>
                </td>
                <td>{new Date(item.last_updated).toLocaleString()}</td>
                <td style={{ display: "flex", gap: 6 }}>
                  <button className="btn btn-primary" style={{ padding: "4px 10px", fontSize: "0.75rem" }}
                    onClick={() => { setStockInId(item.product_id); setStockInQty(""); }}>
                    + Stock In
                  </button>
                  <button className="btn btn-secondary" style={{ padding: "4px 10px", fontSize: "0.75rem" }}
                    onClick={() => { setAdjustId(item.product_id); setNewQty(String(item.quantity_available)); }}>
                    Adjust
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {stockInId && (
        <div className="modal-overlay" onClick={() => setStockInId(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Add Stock</h3>
            <form onSubmit={handleStockIn}>
              <div className="form-group">
                <label>Quantity to add</label>
                <input className="input" type="number" min="1" required value={stockInQty} onChange={(e) => setStockInQty(e.target.value)} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setStockInId(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Add Stock</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {adjustId && (
        <div className="modal-overlay" onClick={() => setAdjustId(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Adjust Stock</h3>
            <form onSubmit={handleAdjust}>
              <div className="form-group">
                <label>New quantity</label>
                <input className="input" type="number" min="0" required value={newQty} onChange={(e) => setNewQty(e.target.value)} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setAdjustId(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Adjustment</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
