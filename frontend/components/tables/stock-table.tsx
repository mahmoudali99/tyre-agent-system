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
import { ArrowUp } from 'lucide-react';
import { StockItem } from '@/lib/api';

interface StockTableProps {
  items: StockItem[];
  onUpdate?: (id: number) => void;
}

export function StockTable({ items, onUpdate }: StockTableProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OK':
        return 'bg-success text-white';
      case 'Low':
        return 'bg-warning text-white';
      case 'Critical':
        return 'bg-destructive text-white';
      default:
        return 'bg-muted text-foreground';
    }
  };

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-secondary border-border hover:bg-secondary">
            <TableHead className="text-foreground">Brand</TableHead>
            <TableHead className="text-foreground">Model</TableHead>
            <TableHead className="text-foreground">Size</TableHead>
            <TableHead className="text-foreground">Current Stock</TableHead>
            <TableHead className="text-foreground">Min Level</TableHead>
            <TableHead className="text-foreground">Status</TableHead>
            <TableHead className="text-foreground">Last Update</TableHead>
            <TableHead className="text-foreground">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item) => (
            <TableRow
              key={item.id}
              className="border-border hover:bg-secondary"
            >
              <TableCell className="text-foreground">{item.brand_name}</TableCell>
              <TableCell className="font-semibold text-foreground">{item.model}</TableCell>
              <TableCell className="text-muted-foreground">{item.size}</TableCell>
              <TableCell className="text-foreground font-semibold">{item.current_stock}</TableCell>
              <TableCell className="text-foreground">{item.min_level}</TableCell>
              <TableCell>
                <Badge className={getStatusColor(item.status)}>{item.status}</Badge>
              </TableCell>
              <TableCell className="text-muted-foreground text-sm">{item.last_update}</TableCell>
              <TableCell>
                <Button
                  size="sm"
                  onClick={() => onUpdate?.(item.id)}
                  className="bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  <ArrowUp className="w-4 h-4 mr-1" />
                  Update
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
