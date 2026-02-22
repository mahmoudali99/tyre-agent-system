'use client';

import { useState, useEffect, useCallback } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { StockTable } from '@/components/tables/stock-table';
import { AlertCircle } from 'lucide-react';
import { getStock, updateTyreStock, StockItem } from '@/lib/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

export default function StockPage() {
  const [items, setItems] = useState<StockItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<StockItem | null>(null);
  const [newStock, setNewStock] = useState('');
  const [search, setSearch] = useState('');

  const toast = (msg: string) => { setToastMessage(msg); setShowToast(true); setTimeout(() => setShowToast(false), 2000); };

  const load = useCallback(() => {
    setLoading(true);
    getStock().then(setItems).catch(() => setItems([])).finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleUpdate = (id: number) => {
    const item = items.find(i => i.id === id);
    if (item) { setEditingItem(item); setNewStock(String(item.current_stock)); setDialogOpen(true); }
  };

  const handleSaveStock = async () => {
    if (!editingItem) return;
    try {
      await updateTyreStock(editingItem.id, Number(newStock));
      toast(`Updated stock for: ${editingItem.brand_name} ${editingItem.model}`);
      setDialogOpen(false);
      load();
    } catch (e: any) { toast(`Error: ${e.message}`); }
  };

  const criticalItems = items.filter(item => item.status === 'Critical' || item.status === 'Low');

  const filtered = items.filter(i =>
    i.brand_name.toLowerCase().includes(search.toLowerCase()) ||
    i.model.toLowerCase().includes(search.toLowerCase()) ||
    i.size.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Stock Management</h1>
          <p className="text-muted-foreground mt-1">Monitor and manage tyre inventory levels</p>
        </div>

        {criticalItems.length > 0 && (
          <div className="bg-destructive bg-opacity-10 border border-destructive text-destructive rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold">{criticalItems.length} items need attention</p>
              <p className="text-sm">Some items are at critical or low stock levels</p>
            </div>
          </div>
        )}

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-4 mb-6">
            <input type="text" placeholder="Search inventory..." value={search} onChange={e => setSearch(e.target.value)}
              className="flex-1 px-4 py-2 rounded-lg border border-border bg-card text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          {loading ? <div className="text-center py-8 text-muted-foreground">Loading...</div> : <StockTable items={filtered} onUpdate={handleUpdate} />}
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent>
            <DialogHeader><DialogTitle>Update Stock</DialogTitle></DialogHeader>
            {editingItem && (
              <div className="space-y-4 py-4">
                <p className="text-sm text-muted-foreground">{editingItem.brand_name} {editingItem.model} ({editingItem.size})</p>
                <div className="space-y-2">
                  <Label>New Stock Level</Label>
                  <Input type="number" value={newStock} onChange={e => setNewStock(e.target.value)} />
                </div>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleSaveStock}>Update</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {showToast && <div className="fixed bottom-4 right-4 bg-success text-white px-6 py-3 rounded-lg shadow-lg z-50">{toastMessage}</div>}
      </div>
    </MainLayout>
  );
}
