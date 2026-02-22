'use client';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Eye, Trash2 } from 'lucide-react';
import { Order, updateOrderStatus } from '@/lib/api';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface OrdersTableProps {
  orders: Order[];
  onViewOrder?: (order: Order) => void;
  onDelete?: (id: number) => void;
  onStatusChange?: () => void;
}

const STATUS_OPTIONS = ['Pending', 'Confirmed', 'Processing', 'Ready', 'Shipped', 'Delivered', 'Completed', 'Cancelled'];

const formatOrderCode = (id: number) => `MTX-${String(id).padStart(5, '0')}`;

export function OrdersTable({ orders, onViewOrder, onDelete, onStatusChange }: OrdersTableProps) {
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
    <div className="border border-border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-secondary border-border hover:bg-secondary">
            <TableHead className="text-foreground">Order Code</TableHead>
            <TableHead className="text-foreground">Customer</TableHead>
            <TableHead className="text-foreground">Date</TableHead>
            <TableHead className="text-foreground">Amount</TableHead>
            <TableHead className="text-foreground">Items</TableHead>
            <TableHead className="text-foreground">Status</TableHead>
            <TableHead className="text-foreground">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {orders.map((order) => (
            <TableRow
              key={order.id}
              className="border-border hover:bg-secondary cursor-pointer"
            >
              <TableCell className="font-semibold text-primary">{formatOrderCode(order.id)}</TableCell>
              <TableCell className="text-foreground">{order.customer_name}</TableCell>
              <TableCell className="text-muted-foreground">{order.created_at ? new Date(order.created_at).toLocaleDateString() : ''}</TableCell>
              <TableCell className="font-semibold text-foreground">£{order.total_amount.toFixed(2)}</TableCell>
              <TableCell className="text-foreground">{order.items_count} items</TableCell>
              <TableCell>
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
                  <SelectTrigger className="w-[130px] h-8 text-xs">
                    <Badge className={getStatusColor(order.status)}>{order.status}</Badge>
                  </SelectTrigger>
                  <SelectContent>
                    {STATUS_OPTIONS.map((s) => (
                      <SelectItem key={s} value={s}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onViewOrder?.(order)}
                    className="text-primary hover:bg-primary hover:text-primary-foreground"
                  >
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete?.(order.id)}
                    className="text-destructive hover:bg-destructive hover:text-white"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
