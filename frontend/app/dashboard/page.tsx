'use client';

import { useEffect, useState } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { StatCard } from '@/components/dashboard/stat-card';
import { getDashboardStats, DashboardStats } from '@/lib/api';
import { ShoppingCart, DollarSign, Box, Zap } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats()
      .then(setStats)
      .catch(() => setStats({ total_orders: 0, total_revenue: 0, tyres_in_stock: 0, car_models: 0 }))
      .finally(() => setLoading(false));
  }, []);

  const s = stats || { total_orders: 0, total_revenue: 0, tyres_in_stock: 0, car_models: 0 };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">Welcome to your Matrax Tyres dashboard</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Orders"
            value={loading ? '...' : s.total_orders}
            icon={ShoppingCart}
            description="All orders"
          />
          <StatCard
            title="Total Revenue"
            value={loading ? '...' : `$${(s.total_revenue / 1000).toFixed(1)}k`}
            icon={DollarSign}
            description="Total sales"
          />
          <StatCard
            title="Tyres in Stock"
            value={loading ? '...' : s.tyres_in_stock}
            icon={Box}
            description="Total inventory"
          />
          <StatCard
            title="Car Models"
            value={loading ? '...' : s.car_models}
            icon={Zap}
            description="Total models"
          />
        </div>

        <div className="bg-card border border-border rounded-lg p-6 mt-8">
          <h2 className="text-xl font-semibold text-foreground mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/orders" className="p-4 border border-border rounded-lg hover:bg-secondary transition-colors text-left">
              <p className="font-semibold text-foreground">New Order</p>
              <p className="text-sm text-muted-foreground">Create a new order</p>
            </Link>
            <Link href="/car-brands" className="p-4 border border-border rounded-lg hover:bg-secondary transition-colors text-left">
              <p className="font-semibold text-foreground">Add Car Brand</p>
              <p className="text-sm text-muted-foreground">Add a new car brand</p>
            </Link>
            <Link href="/stock" className="p-4 border border-border rounded-lg hover:bg-secondary transition-colors text-left">
              <p className="font-semibold text-foreground">Update Stock</p>
              <p className="text-sm text-muted-foreground">Manage inventory levels</p>
            </Link>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
