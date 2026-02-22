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
import { Edit, Trash2 } from 'lucide-react';
import { Tyre } from '@/lib/api';

interface TyresTableProps {
  tyres: Tyre[];
  onEdit?: (tyre: Tyre) => void;
  onDelete?: (id: number) => void;
}

export function TyresTable({ tyres, onEdit, onDelete }: TyresTableProps) {
  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-secondary border-border hover:bg-secondary">
            <TableHead className="text-foreground">Brand</TableHead>
            <TableHead className="text-foreground">Model</TableHead>
            <TableHead className="text-foreground">Size</TableHead>
            <TableHead className="text-foreground">Type</TableHead>
            <TableHead className="text-foreground">Price</TableHead>
            <TableHead className="text-foreground">Stock</TableHead>
            <TableHead className="text-foreground">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tyres.map((tyre) => (
            <TableRow
              key={tyre.id}
              className="border-border hover:bg-secondary"
            >
              <TableCell className="text-foreground">{tyre.brand_name}</TableCell>
              <TableCell className="font-semibold text-foreground">{tyre.model}</TableCell>
              <TableCell className="text-muted-foreground">{tyre.size}</TableCell>
              <TableCell className="text-foreground text-sm">{tyre.type}</TableCell>
              <TableCell className="font-semibold text-foreground">£{tyre.price.toFixed(2)}</TableCell>
              <TableCell>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    tyre.stock > 100
                      ? 'bg-success bg-opacity-20 text-success'
                      : tyre.stock > 50
                      ? 'bg-warning bg-opacity-20 text-warning'
                      : 'bg-destructive bg-opacity-20 text-destructive'
                  }`}
                >
                  {tyre.stock}
                </span>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit?.(tyre)}
                    className="text-primary hover:bg-primary hover:text-primary-foreground"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete?.(tyre.id)}
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
