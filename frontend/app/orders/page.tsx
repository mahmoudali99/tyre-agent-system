'use client';

import { useState, useEffect, useCallback } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { OrdersTable } from '@/components/tables/orders-table';
import { OrderDetailsDrawer } from '@/components/modals/order-details-drawer';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { getOrders, deleteOrder, Order } from '@/lib/api';

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const toast = (msg: string) => { setToastMessage(msg); setShowToast(true); setTimeout(() => setShowToast(false), 2000); };

  const load = useCallback(() => {
    setLoading(true);
    getOrders().then(setOrders).catch(() => setOrders([])).finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleViewOrder = (order: Order) => { setSelectedOrder(order); setDrawerOpen(true); };

  const handleDelete = async (id: number) => {
    if (!confirm(`Delete order #${id}?`)) return;
    try { await deleteOrder(id); toast(`Deleted order #${id}`); load(); } catch (e: any) { toast(`Error: ${e.message}`); }
  };

  const formatOrderCode = (id: number) => `MTX-${String(id).padStart(5, '0')}`;

  const filtered = orders.filter(o => {
    const q = search.toLowerCase();
    const code = formatOrderCode(o.id).toLowerCase();
    return o.customer_name.toLowerCase().includes(q) ||
      String(o.id).includes(q) ||
      code.includes(q);
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Orders</h1>
            <p className="text-muted-foreground mt-1">Manage and track all customer orders</p>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-4 mb-6">
            <input type="text" placeholder="Search orders..." value={search} onChange={e => setSearch(e.target.value)}
              className="flex-1 px-4 py-2 rounded-lg border border-border bg-card text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          {loading ? <div className="text-center py-8 text-muted-foreground">Loading...</div> : <OrdersTable orders={filtered} onViewOrder={handleViewOrder} onDelete={handleDelete} onStatusChange={load} />}
        </div>

        <OrderDetailsDrawer order={selectedOrder} open={drawerOpen} onOpenChange={setDrawerOpen} onStatusChange={load} />
        {showToast && <div className="fixed bottom-4 right-4 bg-success text-white px-6 py-3 rounded-lg shadow-lg z-50">{toastMessage}</div>}
      </div>
    </MainLayout>
  );
}
