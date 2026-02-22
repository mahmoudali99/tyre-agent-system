const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

async function fetchApi(endpoint: string, options?: RequestInit) {
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }
  return res.json();
}

// ---- Dashboard ----
export interface DashboardStats {
  total_orders: number;
  total_revenue: number;
  tyres_in_stock: number;
  car_models: number;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return fetchApi('/dashboard/stats');
}

// ---- Car Brands ----
export interface CarBrand {
  id: number;
  name: string;
  country: string;
  models_count: number;
}

export async function getCarBrands(): Promise<CarBrand[]> {
  return fetchApi('/car-brands');
}

export async function createCarBrand(data: { name: string; country: string }): Promise<CarBrand> {
  return fetchApi('/car-brands', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateCarBrand(id: number, data: { name?: string; country?: string }): Promise<CarBrand> {
  return fetchApi(`/car-brands/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteCarBrand(id: number): Promise<void> {
  return fetchApi(`/car-brands/${id}`, { method: 'DELETE' });
}

// ---- Car Models ----
export interface CarModel {
  id: number;
  brand_id: number;
  brand_name: string;
  name: string;
  year: number;
  tyre_sizes: string[];
}

export async function getCarModels(): Promise<CarModel[]> {
  return fetchApi('/car-models');
}

export async function createCarModel(data: { brand_id: number; name: string; year: number; tyre_sizes: string[] }): Promise<CarModel> {
  return fetchApi('/car-models', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateCarModel(id: number, data: { brand_id?: number; name?: string; year?: number; tyre_sizes?: string[] }): Promise<CarModel> {
  return fetchApi(`/car-models/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteCarModel(id: number): Promise<void> {
  return fetchApi(`/car-models/${id}`, { method: 'DELETE' });
}

// ---- Tyre Brands ----
export interface TyreBrand {
  id: number;
  name: string;
  country: string;
  tyres_count: number;
}

export async function getTyreBrands(): Promise<TyreBrand[]> {
  return fetchApi('/tyre-brands');
}

export async function createTyreBrand(data: { name: string; country: string }): Promise<TyreBrand> {
  return fetchApi('/tyre-brands', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateTyreBrand(id: number, data: { name?: string; country?: string }): Promise<TyreBrand> {
  return fetchApi(`/tyre-brands/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteTyreBrand(id: number): Promise<void> {
  return fetchApi(`/tyre-brands/${id}`, { method: 'DELETE' });
}

// ---- Tyres ----
export interface Tyre {
  id: number;
  brand_id: number;
  brand_name: string;
  model: string;
  size: string;
  type: string;
  price: number;
  cost: number;
  stock: number;
  min_stock_level: number;
}

export async function getTyres(): Promise<Tyre[]> {
  return fetchApi('/tyres');
}

export async function createTyre(data: {
  brand_id: number; model: string; size: string; type: string;
  price: number; cost: number; stock: number; min_stock_level?: number;
}): Promise<Tyre> {
  return fetchApi('/tyres', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateTyre(id: number, data: Partial<Tyre>): Promise<Tyre> {
  return fetchApi(`/tyres/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteTyre(id: number): Promise<void> {
  return fetchApi(`/tyres/${id}`, { method: 'DELETE' });
}

export async function updateTyreStock(id: number, stock: number): Promise<Tyre> {
  return fetchApi(`/tyres/${id}/stock`, { method: 'PUT', body: JSON.stringify({ stock }) });
}

// ---- Stock ----
export interface StockItem {
  id: number;
  brand_name: string;
  model: string;
  size: string;
  current_stock: number;
  min_level: number;
  status: string;
  last_update: string;
}

export async function getStock(): Promise<StockItem[]> {
  return fetchApi('/tyres/stock');
}

// ---- Orders ----
export interface OrderItem {
  id: number;
  tyre_id: number;
  tyre_name: string;
  quantity: number;
  unit_price: number;
}

export interface Order {
  id: number;
  customer_name: string;
  status: string;
  total_amount: number;
  shipping_address?: string;
  payment_method?: string;
  items_count: number;
  items: OrderItem[];
  created_at?: string;
}

export async function getOrders(): Promise<Order[]> {
  return fetchApi('/orders');
}

export async function createOrder(data: {
  customer_name: string;
  shipping_address?: string;
  payment_method?: string;
  items: { tyre_id: number; quantity: number }[];
}): Promise<Order> {
  return fetchApi('/orders', { method: 'POST', body: JSON.stringify(data) });
}

export async function deleteOrder(id: number): Promise<void> {
  return fetchApi(`/orders/${id}`, { method: 'DELETE' });
}

export async function updateOrderStatus(id: number, status: string): Promise<void> {
  return fetchApi(`/orders/${id}/status`, { method: 'PUT', body: JSON.stringify({ status }) });
}

// ---- Chat ----
export interface ChatMessage {
  id: number;
  sender: string;
  text: string;
  timestamp: string;
}

export interface ChatResponse {
  session_id: number;
  message: ChatMessage;
  agent_response: ChatMessage;
}

export async function sendChatMessage(message: string, sessionId?: number): Promise<ChatResponse> {
  return fetchApi('/chat', {
    method: 'POST',
    body: JSON.stringify({ message, session_id: sessionId }),
  });
}

export interface ChatSession {
  id: number;
  title: string;
  created_at: string;
}

export async function getChatSessions(): Promise<ChatSession[]> {
  return fetchApi('/chat/sessions');
}

export async function getSessionMessages(sessionId: number): Promise<ChatMessage[]> {
  return fetchApi(`/chat/sessions/${sessionId}/messages`);
}

// ---- Seed ----
export async function seedDatabase(): Promise<{ status: string; output: string }> {
  return fetchApi('/seed', { method: 'POST' });
}
