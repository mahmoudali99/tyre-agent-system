'use client';

import { useState, useEffect, useCallback } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { CarBrandsTable } from '@/components/tables/car-brands-table';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { getCarBrands, createCarBrand, updateCarBrand, deleteCarBrand, CarBrand } from '@/lib/api';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function CarBrandsPage() {
  const [brands, setBrands] = useState<CarBrand[]>([]);
  const [loading, setLoading] = useState(true);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingBrand, setEditingBrand] = useState<CarBrand | null>(null);
  const [formName, setFormName] = useState('');
  const [formCountry, setFormCountry] = useState('');
  const [search, setSearch] = useState('');

  const toast = (msg: string) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2000);
  };

  const loadBrands = useCallback(() => {
    setLoading(true);
    getCarBrands().then(setBrands).catch(() => setBrands([])).finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadBrands(); }, [loadBrands]);

  const openCreate = () => {
    setEditingBrand(null);
    setFormName('');
    setFormCountry('');
    setDialogOpen(true);
  };

  const openEdit = (brand: CarBrand) => {
    setEditingBrand(brand);
    setFormName(brand.name);
    setFormCountry(brand.country);
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      if (editingBrand) {
        await updateCarBrand(editingBrand.id, { name: formName, country: formCountry });
        toast(`Updated: ${formName}`);
      } else {
        await createCarBrand({ name: formName, country: formCountry });
        toast(`Created: ${formName}`);
      }
      setDialogOpen(false);
      loadBrands();
    } catch (e: any) {
      toast(`Error: ${e.message}`);
    }
  };

  const handleDelete = async (id: number) => {
    const brand = brands.find(b => b.id === id);
    if (!confirm(`Delete ${brand?.name}?`)) return;
    try {
      await deleteCarBrand(id);
      toast(`Deleted: ${brand?.name}`);
      loadBrands();
    } catch (e: any) {
      toast(`Error: ${e.message}`);
    }
  };

  const filtered = brands.filter(b =>
    b.name.toLowerCase().includes(search.toLowerCase()) ||
    b.country.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Car Brands</h1>
            <p className="text-muted-foreground mt-1">Manage all car brands in the system</p>
          </div>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90" onClick={openCreate}>
            <Plus className="w-4 h-4 mr-2" />
            Add Brand
          </Button>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-4 mb-6">
            <input
              type="text"
              placeholder="Search brands..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 px-4 py-2 rounded-lg border border-border bg-card text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading...</div>
          ) : (
            <CarBrandsTable brands={filtered} onEdit={openEdit} onDelete={handleDelete} />
          )}
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingBrand ? 'Edit Car Brand' : 'Add Car Brand'}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Brand Name</Label>
                <Input value={formName} onChange={e => setFormName(e.target.value)} placeholder="e.g. Toyota" />
              </div>
              <div className="space-y-2">
                <Label>Country</Label>
                <Input value={formCountry} onChange={e => setFormCountry(e.target.value)} placeholder="e.g. Japan" />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleSave} disabled={!formName || !formCountry}>Save</Button>
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
