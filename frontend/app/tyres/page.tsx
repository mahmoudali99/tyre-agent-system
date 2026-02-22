'use client';

import { useState, useEffect, useCallback } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { TyresTable } from '@/components/tables/tyres-table';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { getTyres, getTyreBrands, createTyre, updateTyre, deleteTyre, Tyre, TyreBrand } from '@/lib/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function TyresPage() {
  const [tyres, setTyres] = useState<Tyre[]>([]);
  const [brands, setBrands] = useState<TyreBrand[]>([]);
  const [loading, setLoading] = useState(true);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Tyre | null>(null);
  const [form, setForm] = useState({ brand_id: '', model: '', size: '', type: '', price: '', cost: '', stock: '', min_stock_level: '50' });
  const [search, setSearch] = useState('');

  const toast = (msg: string) => { setToastMessage(msg); setShowToast(true); setTimeout(() => setShowToast(false), 2000); };

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([getTyres(), getTyreBrands()])
      .then(([t, b]) => { setTyres(t); setBrands(b); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const openCreate = () => {
    setEditing(null);
    setForm({ brand_id: '', model: '', size: '', type: '', price: '', cost: '', stock: '', min_stock_level: '50' });
    setDialogOpen(true);
  };

  const openEdit = (t: Tyre) => {
    setEditing(t);
    setForm({
      brand_id: String(t.brand_id), model: t.model, size: t.size, type: t.type,
      price: String(t.price), cost: String(t.cost), stock: String(t.stock), min_stock_level: String(t.min_stock_level),
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    const data = {
      brand_id: Number(form.brand_id), model: form.model, size: form.size, type: form.type,
      price: Number(form.price), cost: Number(form.cost), stock: Number(form.stock), min_stock_level: Number(form.min_stock_level),
    };
    try {
      if (editing) { await updateTyre(editing.id, data); toast(`Updated: ${form.model}`); }
      else { await createTyre(data); toast(`Created: ${form.model}`); }
      setDialogOpen(false); load();
    } catch (e: any) { toast(`Error: ${e.message}`); }
  };

  const handleDelete = async (id: number) => {
    const t = tyres.find(x => x.id === id);
    if (!confirm(`Delete ${t?.brand_name} ${t?.model}?`)) return;
    try { await deleteTyre(id); toast(`Deleted: ${t?.model}`); load(); } catch (e: any) { toast(`Error: ${e.message}`); }
  };

  const filtered = tyres.filter(t =>
    t.model.toLowerCase().includes(search.toLowerCase()) ||
    t.brand_name.toLowerCase().includes(search.toLowerCase()) ||
    t.size.toLowerCase().includes(search.toLowerCase())
  );

  const setField = (key: string, val: string) => setForm(prev => ({ ...prev, [key]: val }));

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Tyres</h1>
            <p className="text-muted-foreground mt-1">Manage tyre inventory and pricing</p>
          </div>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90" onClick={openCreate}>
            <Plus className="w-4 h-4 mr-2" />
            Add Tyre
          </Button>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-4 mb-6">
            <input type="text" placeholder="Search tyres..." value={search} onChange={e => setSearch(e.target.value)}
              className="flex-1 px-4 py-2 rounded-lg border border-border bg-card text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          {loading ? <div className="text-center py-8 text-muted-foreground">Loading...</div> : <TyresTable tyres={filtered} onEdit={openEdit} onDelete={handleDelete} />}
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="max-w-lg">
            <DialogHeader><DialogTitle>{editing ? 'Edit Tyre' : 'Add Tyre'}</DialogTitle></DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Brand</Label>
                <Select value={form.brand_id} onValueChange={v => setField('brand_id', v)}>
                  <SelectTrigger><SelectValue placeholder="Select brand" /></SelectTrigger>
                  <SelectContent>{brands.map(b => <SelectItem key={b.id} value={String(b.id)}>{b.name}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2"><Label>Model</Label><Input value={form.model} onChange={e => setField('model', e.target.value)} placeholder="e.g. Pilot Sport 4" /></div>
                <div className="space-y-2"><Label>Size</Label><Input value={form.size} onChange={e => setField('size', e.target.value)} placeholder="e.g. 225/45R17" /></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2"><Label>Type</Label><Input value={form.type} onChange={e => setField('type', e.target.value)} placeholder="e.g. Performance" /></div>
                <div className="space-y-2"><Label>Price</Label><Input type="number" value={form.price} onChange={e => setField('price', e.target.value)} /></div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2"><Label>Cost</Label><Input type="number" value={form.cost} onChange={e => setField('cost', e.target.value)} /></div>
                <div className="space-y-2"><Label>Stock</Label><Input type="number" value={form.stock} onChange={e => setField('stock', e.target.value)} /></div>
                <div className="space-y-2"><Label>Min Stock</Label><Input type="number" value={form.min_stock_level} onChange={e => setField('min_stock_level', e.target.value)} /></div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleSave} disabled={!form.brand_id || !form.model || !form.size}>Save</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {showToast && <div className="fixed bottom-4 right-4 bg-success text-white px-6 py-3 rounded-lg shadow-lg z-50">{toastMessage}</div>}
      </div>
    </MainLayout>
  );
}
