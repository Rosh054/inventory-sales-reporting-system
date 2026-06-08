import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import { api, SalesSummary, RevenueByCategory, TopProduct, InventoryValuation, Sale } from "../api/client";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16"];

function formatCurrency(val: string | number) {
  return `$${Number(val).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<SalesSummary | null>(null);
  const [valuation, setValuation] = useState<InventoryValuation | null>(null);
  const [categories, setCategories] = useState<RevenueByCategory[]>([]);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const [lowStockCount, setLowStockCount] = useState(0);
  const [recentSales, setRecentSales] = useState<Sale[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.reports.salesSummary(),
      api.reports.inventoryValuation(),
      api.reports.revenueByCategory(),
      api.reports.topProducts(5),
      api.reports.lowStock(),
      api.sales.list(),
    ]).then(([s, v, c, t, l, sales]) => {
      setSummary(s);
      setValuation(v);
      setCategories(c);
      setTopProducts(t);
      setLowStockCount(l.length);
      setRecentSales(sales.slice(0, 8));
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading dashboard...</div>;

  const categoryData = categories.map((c) => ({
    name: c.category,
    revenue: Number(c.revenue),
  }));

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Business overview — revenue, inventory, and sales at a glance</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="label">Total Revenue</div>
          <div className="value">{summary ? formatCurrency(summary.total_revenue) : "—"}</div>
          <div className="sub">{summary?.total_sales ?? 0} total sales</div>
        </div>
        <div className="stat-card">
          <div className="label">Avg Order Value</div>
          <div className="value">{summary ? formatCurrency(summary.average_order_value) : "—"}</div>
        </div>
        <div className="stat-card">
          <div className="label">Low Stock Items</div>
          <div className="value" style={{ color: lowStockCount > 0 ? "#ef4444" : "#10b981" }}>
            {lowStockCount}
          </div>
          <div className="sub">At or below reorder level</div>
        </div>
        <div className="stat-card">
          <div className="label">Inventory Valuation</div>
          <div className="value">{valuation ? formatCurrency(valuation.total_retail_value) : "—"}</div>
          <div className="sub">{valuation?.total_units ?? 0} units in stock</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="card">
          <h3 style={{ marginBottom: 16, fontSize: "0.95rem", fontWeight: 600 }}>Revenue by Category</h3>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={categoryData} dataKey="revenue" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                  {categoryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v: number) => formatCurrency(v)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : <p style={{ color: "#94a3b8" }}>No sales data yet</p>}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 16, fontSize: "0.95rem", fontWeight: 600 }}>Top 5 Products by Revenue</h3>
          {topProducts.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={topProducts.map((p) => ({ name: p.product_name.slice(0, 20), revenue: Number(p.revenue) }))} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={(v) => `$${v}`} />
                <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => formatCurrency(v)} />
                <Bar dataKey="revenue" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <p style={{ color: "#94a3b8" }}>No product sales yet</p>}
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: 16, fontSize: "0.95rem", fontWeight: 600 }}>Recent Sales</h3>
        <table>
          <thead>
            <tr>
              <th>Sale ID</th>
              <th>Customer</th>
              <th>Date</th>
              <th>Payment</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {recentSales.map((s) => (
              <tr key={s.sale_id}>
                <td>#{s.sale_id}</td>
                <td>{s.customer_name || "Walk-in"}</td>
                <td>{new Date(s.sale_timestamp).toLocaleDateString()}</td>
                <td><span className="badge badge-green">{s.payment_method}</span></td>
                <td>{formatCurrency(s.total_amount)}</td>
              </tr>
            ))}
            {recentSales.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: "center", color: "#94a3b8" }}>No sales yet</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
