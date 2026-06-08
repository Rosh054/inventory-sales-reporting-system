import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import {
  api, ProfitSummary, MonthlySales, SupplierPerformance, LowStockItem,
} from "../api/client";

function formatCurrency(val: string | number) {
  return `$${Number(val).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function ReportsPage() {
  const [profit, setProfit] = useState<ProfitSummary | null>(null);
  const [monthly, setMonthly] = useState<MonthlySales[]>([]);
  const [suppliers, setSuppliers] = useState<SupplierPerformance[]>([]);
  const [lowStock, setLowStock] = useState<LowStockItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.reports.profitSummary(),
      api.reports.monthlySales(),
      api.reports.supplierPerformance(),
      api.reports.lowStock(),
    ]).then(([p, m, s, l]) => {
      setProfit(p);
      setMonthly(m);
      setSuppliers(s);
      setLowStock(l);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading reports...</div>;

  const monthlyData = monthly.map((m) => ({
    month: m.month,
    revenue: Number(m.revenue),
    sales: m.sales_count,
  }));

  return (
    <div>
      <div className="page-header">
        <h2>Reports</h2>
        <p>SQL-backed business analytics and data exports</p>
      </div>

      <div className="toolbar">
        <a href={api.exports.salesCsv()} className="btn btn-secondary" download>Export Sales CSV</a>
        <a href={api.exports.inventoryCsv()} className="btn btn-secondary" download>Export Inventory CSV</a>
        <a href={api.exports.lowStockCsv()} className="btn btn-secondary" download>Export Low Stock CSV</a>
      </div>

      {profit && (
        <div className="stats-grid" style={{ marginBottom: 24 }}>
          <div className="stat-card">
            <div className="label">Total Revenue</div>
            <div className="value">{formatCurrency(profit.total_revenue)}</div>
          </div>
          <div className="stat-card">
            <div className="label">Total Cost</div>
            <div className="value">{formatCurrency(profit.total_cost)}</div>
          </div>
          <div className="stat-card">
            <div className="label">Total Profit</div>
            <div className="value" style={{ color: "#10b981" }}>{formatCurrency(profit.total_profit)}</div>
          </div>
          <div className="stat-card">
            <div className="label">Profit Margin</div>
            <div className="value">{profit.profit_margin_pct}%</div>
          </div>
        </div>
      )}

      <div className="charts-grid">
        <div className="card">
          <h3 style={{ marginBottom: 16, fontSize: "0.95rem", fontWeight: 600 }}>Monthly Sales Trend</h3>
          {monthlyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={(v) => `$${v}`} />
                <Tooltip formatter={(v: number, name: string) => name === "revenue" ? formatCurrency(v) : v} />
                <Legend />
                <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" radius={[4, 4, 0, 0]} />
                <Bar dataKey="sales" fill="#10b981" name="Sales Count" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <p style={{ color: "#94a3b8" }}>No monthly data</p>}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 16, fontSize: "0.95rem", fontWeight: 600 }}>Supplier Performance</h3>
          <table>
            <thead>
              <tr><th>Supplier</th><th>Products</th><th>Units Sold</th><th>Revenue</th></tr>
            </thead>
            <tbody>
              {suppliers.map((s) => (
                <tr key={s.supplier_id}>
                  <td>{s.supplier_name}</td>
                  <td>{s.product_count}</td>
                  <td>{s.units_sold}</td>
                  <td>{formatCurrency(s.revenue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3 style={{ marginBottom: 16, fontSize: "0.95rem", fontWeight: 600 }}>
          Low Stock Alert ({lowStock.length} items)
        </h3>
        <table>
          <thead>
            <tr><th>SKU</th><th>Product</th><th>Available</th><th>Reorder Level</th></tr>
          </thead>
          <tbody>
            {lowStock.map((item) => (
              <tr key={item.product_id}>
                <td><code>{item.sku}</code></td>
                <td>{item.product_name}</td>
                <td><span className="badge badge-red">{item.quantity_available}</span></td>
                <td>{item.reorder_level}</td>
              </tr>
            ))}
            {lowStock.length === 0 && (
              <tr><td colSpan={4} style={{ textAlign: "center", color: "#10b981" }}>All stock levels healthy</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
