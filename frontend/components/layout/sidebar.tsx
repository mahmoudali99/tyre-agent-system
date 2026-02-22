'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BarChart3, ShoppingCart, Truck, Wrench, Boxes, Package, MessageSquare, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Orders', href: '/orders', icon: ShoppingCart },
  { name: 'Car Brands', href: '/car-brands', icon: Truck },
  { name: 'Car Models', href: '/car-models', icon: Wrench },
  { name: 'Tyre Brands', href: '/tyre-brands', icon: Package },
  { name: 'Tyres', href: '/tyres', icon: Boxes },
  { name: 'Stock', href: '/stock', icon: BarChart3 },
  { name: 'Agent Chat', href: '/agent-chat', icon: MessageSquare },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-border bg-card min-h-screen flex flex-col sticky top-0">
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold text-primary">Matrax Tyres</h1>
        <p className="text-sm text-muted-foreground">Multi-Agent System</p>
      </div>
      
      <nav className="flex-1 overflow-y-auto p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-foreground hover:bg-secondary'
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
