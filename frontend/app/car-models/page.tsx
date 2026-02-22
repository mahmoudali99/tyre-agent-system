'use client';

import { useState, useEffect, useCallback } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { CarModelsTable } from '@/components/tables/car-models-table';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { getCarModels, getCarBrands, createCarModel, updateCarModel, deleteCarModel, CarModel, CarBrand } from '@/lib/api';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';

export default function CarModelsPage() {
  const [models, setModels] = useState<CarModel[]>([]);
  const [brands, setBrands] = useState<CarBrand[]>([]);
  const [loading, setLoading] = useState(true);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<CarModel | null>(null);
  const [formBrandId, setFormBrandId] = useState('');
  const [formName, setFormName] = useState('');
  const [formYear, setFormYear] = useState('2024');
  const [formTyreSizes, setFormTyreSizes] = useState('');
  const [search, setSearch] = useState('');

  const toast = (msg: string) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2000);
  };

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([getCarModels(), getCarBrands()])
      .then(([m, b]) => { setModels(m); setBrands(b); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const openCreate = () => {
    setEditing(null);
    setFormBrandId('');
    setFormName('');
    setFormYear('2024');
    setFormTyreSizes('');
    setDialogOpen(true);
  };

  const openEdit = (model: CarModel) => {
    setEditing(model);
    setFormBrandId(String(model.brand_id));
    setFormName(model.name);
    setFormYear(String(model.year));
    setFormTyreSizes((model.tyre_sizes || []).join(', '));
    setDialogOpen(true);
  };

  const handleSave = async () => {
    const sizes = formTyreSizes.split(',').map(s => s.trim()).filter(Boolean);
    try {
      if (editing) {
        await updateCarModel(editing.id, { brand_id: Number(formBrandId), name: formName, year: Number(formYear), tyre_sizes: sizes });
        toast(`Updated: ${formName}`);
      } else {
        await createCarModel({ brand_id: Number(formBrandId), name: formName, year: Number(formYear), tyre_sizes: sizes });
        toast(`Created: ${formName}`);
      }
      setDialogOpen(false);
      load();
    } catch (e: any) {
      toast(`Error: ${e.message}`);
    }
  };

  const handleDelete = async (id: number) => {
    const model = models.find(m => m.id === id);
    if (!confirm(`Delete ${model?.brand_name} ${model?.name}?`)) return;
    try {
      await deleteCarModel(id);
      toast(`Deleted: ${model?.name}`);
      load();
    } catch (e: any) {
      toast(`Error: ${e.message}`);
    }
  };

  const filtered = models.filter(m =>
    m.name.toLowerCase().includes(search.toLowerCase()) ||
    m.brand_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Car Models</h1>
            <p className="text-muted-foreground mt-1">Manage car models and their specifications</p>
          </div>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90" onClick={openCreate}>
            <Plus className="w-4 h-4 mr-2" />
            Add Model
          </Button>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-4 mb-6">
            <input
              type="text"
              placeholder="Search models..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="flex-1 px-4 py-2 rounded-lg border border-border bg-card text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading...</div>
          ) : (
            <CarModelsTable models={filtered} onEdit={openEdit} onDelete={handleDelete} />
          )}
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editing ? 'Edit Car Model' : 'Add Car Model'}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Brand</Label>
                <Select value={formBrandId} onValueChange={setFormBrandId}>
                  <SelectTrigger><SelectValue placeholder="Select brand" /></SelectTrigger>
                  <SelectContent>
                    {brands.map(b => (
                      <SelectItem key={b.id} value={String(b.id)}>{b.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Model Name</Label>
                <Input value={formName} onChange={e => setFormName(e.target.value)} placeholder="e.g. Corolla" />
              </div>
              <div className="space-y-2">
                <Label>Year</Label>
                <Input type="number" value={formYear} onChange={e => setFormYear(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Tyre Sizes (comma-separated)</Label>
                <Input value={formTyreSizes} onChange={e => setFormTyreSizes(e.target.value)} placeholder="e.g. 205/55R16, 215/55R16" />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleSave} disabled={!formBrandId || !formName}>Save</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {showToast && (
          <div className="fixed bottom-4 right-4 bg-success text-white px-6 py-3 rounded-lg shadow-lg z-50">
            {toastMessage}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
