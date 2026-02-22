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
import { CarModel } from '@/lib/api';

interface CarModelsTableProps {
  models: CarModel[];
  onEdit?: (model: CarModel) => void;
  onDelete?: (id: number) => void;
}

export function CarModelsTable({ models, onEdit, onDelete }: CarModelsTableProps) {
  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-secondary border-border hover:bg-secondary">
            <TableHead className="text-foreground">Brand</TableHead>
            <TableHead className="text-foreground">Model</TableHead>
            <TableHead className="text-foreground">Year</TableHead>
            <TableHead className="text-foreground">Tyre Sizes</TableHead>
            <TableHead className="text-foreground">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {models.map((model) => (
            <TableRow
              key={model.id}
              className="border-border hover:bg-secondary"
            >
              <TableCell className="text-foreground">{model.brand_name}</TableCell>
              <TableCell className="font-semibold text-foreground">{model.name}</TableCell>
              <TableCell className="text-muted-foreground">{model.year}</TableCell>
              <TableCell className="text-sm text-foreground">
                <div className="flex flex-wrap gap-1">
                  {(model.tyre_sizes || []).map((size, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-secondary rounded text-xs text-foreground"
                    >
                      {size}
                    </span>
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit?.(model)}
                    className="text-primary hover:bg-primary hover:text-primary-foreground"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete?.(model.id)}
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
