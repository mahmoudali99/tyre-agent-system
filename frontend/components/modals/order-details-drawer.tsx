'use client';

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Order, updateOrderStatus } from '@/lib/api';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { User, Calendar, Package, CreditCard, MapPin, Hash } from 'lucide-react';

const STATUS_OPTIONS = ['Pending', 'Confirmed', 'Processing', 'Ready', 'Shipped', 'Delivered', 'Completed', 'Cancelled'];

const formatOrderCode = (id: number) => `MTX-${String(id).padStart(5, '0')}`;

interface OrderDetailsDrawerProps {
  order: Order | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onStatusChange?: () => void;
}

export function OrderDetailsDrawer({
  order,
  open,
  onOpenChange,
  onStatusChange,
}: OrderDetailsDrawerProps) {
  if (!order) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Delivered':
      case 'Completed':
        return 'bg-green-600 text-white';
      case 'Processing':
      case 'Shipped':
        return 'bg-blue-600 text-white';
      case 'Pending':
        return 'bg-amber-600 text-white';
      case 'Confirmed':
      case 'Ready':
        return 'bg-indigo-600 text-white';
      case 'Cancelled':
        return 'bg-red-600 text-white';
      default:
        return 'bg-gray-600 text-white';
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-xl bg-card border-l border-border overflow-y-auto">
        <SheetHeader className="border-b border-border pb-4">
          <div className="flex items-center justify-between">
            <SheetTitle className="text-2xl font-bold text-foreground flex items-center gap-2">
              <Hash className="w-6 h-6 text-primary" />
              {formatOrderCode(order.id)}
            </SheetTitle>
            <Select
              value={order.status}
              onValueChange={async (value) => {
                try {
                  await updateOrderStatus(order.id, value);
                  onStatusChange?.();
                } catch (e) {
                  console.error('Failed to update status', e);
                }
              }}
            >
              <SelectTrigger className="w-[150px] h-9">
                <Badge className={getStatusColor(order.status)}>{order.status}</Badge>
              </SelectTrigger>
              <SelectContent>
                {STATUS_OPTIONS.map((s) => (
                  <SelectItem key={s} value={s}>{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </SheetHeader>

        <div className="space-y-6 mt-6 pb-6">
          {/* Customer & Date Info */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-secondary/50 rounded-lg p-4 border border-border">
              <div className="flex items-center gap-2 mb-2">
                <User className="w-4 h-4 text-primary" />
                <span className="text-xs font-medium text-muted-foreground uppercase">Customer</span>
              </div>
              <p className="text-foreground font-semibold">{order.customer_name}</p>
            </div>
            <div className="bg-secondary/50 rounded-lg p-4 border border-border">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="w-4 h-4 text-primary" />
                <span className="text-xs font-medium text-muted-foreground uppercase">Order Date</span>
              </div>
              <p className="text-foreground font-semibold">{order.created_at ? new Date(order.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'}</p>
            </div>
          </div>

          {/* Total Amount */}
          <div className="bg-gradient-to-br from-primary/10 to-primary/5 rounded-lg p-5 border border-primary/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Total Amount</p>
                <p className="text-3xl font-bold text-foreground">£{order.total_amount.toFixed(2)}</p>
              </div>
              <div className="bg-primary/10 rounded-full p-3">
                <CreditCard className="w-6 h-6 text-primary" />
              </div>
            </div>
          </div>

          {/* Items Ordered */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Package className="w-5 h-5 text-primary" />
              <h3 className="text-lg font-semibold text-foreground">Items Ordered</h3>
            </div>
            <div className="space-y-3">
              {(order.items || []).map((item, idx) => (
                <div
                  key={idx}
                  className="bg-secondary/50 rounded-lg p-4 border border-border hover:border-primary/30 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <p className="font-semibold text-foreground">{item.tyre_name}</p>
                      <p className="text-sm text-muted-foreground mt-1">Quantity: {item.quantity}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">Unit Price</p>
                      <p className="font-bold text-foreground">£{item.unit_price.toFixed(2)}</p>
                    </div>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-border/50">
                    <span className="text-xs text-muted-foreground">Subtotal</span>
                    <span className="font-semibold text-primary">£{(item.unit_price * item.quantity).toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Shipping & Payment */}
          {(order.shipping_address || order.payment_method) && (
            <div className="space-y-4">
              {order.shipping_address && (
                <div className="bg-secondary/50 rounded-lg p-4 border border-border">
                  <div className="flex items-center gap-2 mb-2">
                    <MapPin className="w-4 h-4 text-primary" />
                    <h3 className="font-semibold text-foreground">Shipping Address</h3>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {order.shipping_address}
                  </p>
                </div>
              )}

              {order.payment_method && (
                <div className="bg-secondary/50 rounded-lg p-4 border border-border">
                  <div className="flex items-center gap-2 mb-2">
                    <CreditCard className="w-4 h-4 text-primary" />
                    <h3 className="font-semibold text-foreground">Payment Method</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {order.payment_method}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
