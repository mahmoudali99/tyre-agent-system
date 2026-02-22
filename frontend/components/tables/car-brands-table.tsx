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
import { CarBrand } from '@/lib/api';

interface CarBrandsTableProps {
  brands: CarBrand[];
  onEdit?: (brand: CarBrand) => void;
  onDelete?: (id: number) => void;
}

export function CarBrandsTable({ brands, onEdit, onDelete }: CarBrandsTableProps) {
  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-secondary border-border hover:bg-secondary">
            <TableHead className="text-foreground">Brand Name</TableHead>
            <TableHead className="text-foreground">Country</TableHead>
            <TableHead className="text-foreground">Car Models</TableHead>
            <TableHead className="text-foreground">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {brands.map((brand) => (
            <TableRow
              key={brand.id}
              className="border-border hover:bg-secondary"
            >
              <TableCell className="font-semibold text-foreground">{brand.name}</TableCell>
              <TableCell className="text-muted-foreground">{brand.country}</TableCell>
              <TableCell className="text-foreground">{brand.models_count}</TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit?.(brand)}
                    className="text-primary hover:bg-primary hover:text-primary-foreground"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete?.(brand.id)}
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
