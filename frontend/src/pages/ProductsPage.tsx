import { useEffect, useState } from "react";
import { api, Product, Supplier } from "../api/client";

const CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys", "Food", "Health"];

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    sku: "", name: "", category: "Electronics",
    unit_price: "", cost_price: "", supplier_id: "", reorder_level: "10",
  });

  const load = () => {
    api.products.list({ search: search || undefined, category: category || undefined })
      .then(setProducts);
  };

  useEffect(() => {
    api.suppliers.list().then(setSuppliers);
    load();
  }, []);

  useEffect(() => { load(); }, [search, category]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await api.products.create({
        sku: form.sku,
        name: form.name,
        category: form.category,
        unit_price: parseFloat(form.unit_price),
        cost_price: parseFloat(form.cost_price),
        supplier_id: parseInt(form.supplier_id),
        reorder_level: parseInt(form.reorder_level),
      });
      setShowModal(false);
      setForm({ sku: "", name: "", category: "Electronics", unit_price: "", cost_price: "", supplier_id: "", reorder_level: "10" });
      load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create product");
    }
  };

  const handleDeactivate = async (id: number) => {
    if (!confirm("Deactivate this product?")) return;
    await api.products.deactivate(id);
    load();
  };

  return (
    <div>
      <div className="page-header">
        <h2>Products</h2>
        <p>Manage product catalog, pricing, and supplier links</p>
      </div>

      <div className="toolbar">
        <input className="input" placeholder="Search by name or SKU..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <select className="select" value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All Categories</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Product</button>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>SKU</th><th>Name</th><th>Category</th>
              <th>Unit Price</th><th>Cost</th><th>Reorder</th><th>Status</th><th></th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.product_id}>
                <td><code>{p.sku}</code></td>
                <td>{p.name}</td>
                <td>{p.category}</td>
                <td>${Number(p.unit_price).toFixed(2)}</td>
                <td>${Number(p.cost_price).toFixed(2)}</td>
                <td>{p.reorder_level}</td>
                <td>
                  <span className={`badge ${p.active ? "badge-green" : "badge-red"}`}>
                    {p.active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td>
                  {p.active && (
                    <button className="btn btn-danger" style={{ padding: "4px 10px", fontSize: "0.75rem" }}
                      onClick={() => handleDeactivate(p.product_id)}>
                      Deactivate
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Add New Product</h3>
            {error && <div className="error-msg">{error}</div>}
            <form onSubmit={handleCreate}>
              <div className="form-grid">
                <div className="form-group">
                  <label>SKU</label>
                  <input className="input" required value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Name</label>
                  <input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Category</label>
                  <select className="select" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                    {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Supplier</label>
                  <select className="select" required value={form.supplier_id} onChange={(e) => setForm({ ...form, supplier_id: e.target.value })}>
                    <option value="">Select supplier</option>
                    {suppliers.map((s) => <option key={s.supplier_id} value={s.supplier_id}>{s.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Unit Price ($)</label>
                  <input className="input" type="number" step="0.01" min="0.01" required value={form.unit_price} onChange={(e) => setForm({ ...form, unit_price: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Cost Price ($)</label>
                  <input className="input" type="number" step="0.01" min="0" required value={form.cost_price} onChange={(e) => setForm({ ...form, cost_price: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Reorder Level</label>
                  <input className="input" type="number" min="0" value={form.reorder_level} onChange={(e) => setForm({ ...form, reorder_level: e.target.value })} />
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create Product</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
