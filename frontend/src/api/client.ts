const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  products: {
    list: (params?: { search?: string; category?: string }) => {
      const qs = new URLSearchParams();
      if (params?.search) qs.set("search", params.search);
      if (params?.category) qs.set("category", params.category);
      const q = qs.toString();
      return request<Product[]>(`/products${q ? `?${q}` : ""}`);
    },
    create: (data: ProductCreate) =>
      request<Product>("/products", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: Partial<ProductCreate>) =>
      request<Product>(`/products/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    deactivate: (id: number) =>
      request<Product>(`/products/${id}`, { method: "DELETE" }),
  },

  suppliers: {
    list: () => request<Supplier[]>("/suppliers"),
  },

  inventory: {
    list: () => request<InventoryItem[]>("/inventory"),
    lowStock: () => request<LowStockItem[]>("/inventory/low-stock"),
    stockIn: (productId: number, quantity: number, reason: string) =>
      request(`/inventory/${productId}/stock-in`, {
        method: "POST",
        body: JSON.stringify({ quantity, reason }),
      }),
    adjust: (productId: number, newQuantity: number, reason: string) =>
      request(`/inventory/${productId}/adjust`, {
        method: "POST",
        body: JSON.stringify({ new_quantity: newQuantity, reason }),
      }),
  },

  sales: {
    list: () => request<Sale[]>("/sales"),
    create: (data: SaleCreate) =>
      request<Sale>("/sales", { method: "POST", body: JSON.stringify(data) }),
  },

  reports: {
    salesSummary: () => request<SalesSummary>("/reports/sales-summary"),
    revenueByCategory: () => request<RevenueByCategory[]>("/reports/revenue-by-category"),
    topProducts: (limit = 5) => request<TopProduct[]>(`/reports/top-products?limit=${limit}`),
    lowStock: () => request<LowStockItem[]>("/reports/low-stock"),
    profitSummary: () => request<ProfitSummary>("/reports/profit-summary"),
    monthlySales: () => request<MonthlySales[]>("/reports/monthly-sales"),
    inventoryValuation: () => request<InventoryValuation>("/reports/inventory-valuation"),
    supplierPerformance: () => request<SupplierPerformance[]>("/reports/supplier-performance"),
  },

  exports: {
    salesCsv: () => `${API_BASE}/exports/sales.csv`,
    inventoryCsv: () => `${API_BASE}/exports/inventory.csv`,
    lowStockCsv: () => `${API_BASE}/exports/low-stock.csv`,
  },
};

export interface Product {
  product_id: number;
  sku: string;
  name: string;
  category: string;
  unit_price: string;
  cost_price: string;
  supplier_id: number;
  reorder_level: number;
  active: boolean;
  created_at: string;
}

export interface ProductCreate {
  sku: string;
  name: string;
  category: string;
  unit_price: number;
  cost_price: number;
  supplier_id: number;
  reorder_level?: number;
}

export interface Supplier {
  supplier_id: number;
  name: string;
  email: string;
  phone: string;
  region: string;
}

export interface InventoryItem {
  inventory_id: number;
  product_id: number;
  quantity_available: number;
  last_updated: string;
  product_name?: string;
  sku?: string;
  reorder_level?: number;
}

export interface LowStockItem {
  product_id: number;
  sku: string;
  product_name: string;
  quantity_available: number;
  reorder_level: number;
}

export interface Sale {
  sale_id: number;
  customer_name: string | null;
  sale_timestamp: string;
  payment_method: string;
  total_amount: string;
  items: SaleItem[];
}

export interface SaleItem {
  sale_item_id: number;
  product_id: number;
  quantity: number;
  unit_price: string;
  line_total: string;
  product_name?: string;
}

export interface SaleCreate {
  customer_name?: string;
  payment_method: string;
  items: { product_id: number; quantity: number }[];
}

export interface SalesSummary {
  total_sales: number;
  total_revenue: string;
  average_order_value: string;
}

export interface RevenueByCategory {
  category: string;
  revenue: string;
  units_sold: number;
}

export interface TopProduct {
  product_id: number;
  product_name: string;
  sku: string;
  units_sold: number;
  revenue: string;
}

export interface ProfitSummary {
  total_revenue: string;
  total_cost: string;
  total_profit: string;
  profit_margin_pct: string;
}

export interface MonthlySales {
  month: string;
  sales_count: number;
  revenue: string;
}

export interface InventoryValuation {
  total_units: number;
  total_cost_value: string;
  total_retail_value: string;
}

export interface SupplierPerformance {
  supplier_id: number;
  supplier_name: string;
  product_count: number;
  units_sold: number;
  revenue: string;
}
