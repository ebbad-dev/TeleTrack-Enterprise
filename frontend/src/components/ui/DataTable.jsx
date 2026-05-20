import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  useReactTable, getCoreRowModel, getSortedRowModel,
  getFilteredRowModel, getPaginationRowModel, flexRender,
} from '@tanstack/react-table';
import { ChevronDown, ChevronUp, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Edit, Trash2, Download } from 'lucide-react';
import { Card } from './Card';
import { Button } from './Button';

export function DataTable({ columns: initialColumns, data, loading, globalFilter, setGlobalFilter, noDataMessage = "NO RECORDS FOUND", onEdit, onDelete, onExport }) {

  const [exportOpen, setExportOpen] = useState(false);

  const columns = React.useMemo(() => {
    let cols = [...initialColumns];
    if (onEdit || onDelete) {
      cols.push({
        id: 'actions', header: 'Actions', size: 90,
        cell: (info) => (
          <div className="flex items-center space-x-1">
            {onEdit && (
              <button onClick={() => onEdit(info.row.original)}
                className="p-1.5 text-textMuted hover:text-primary transition-colors rounded-lg hover:bg-primary/10">
                <Edit size={14} />
              </button>
            )}
            {onDelete && (
              <button onClick={() => onDelete(info.row.original.id || info.row.original.device_id)}
                className="p-1.5 text-textMuted hover:text-error transition-colors rounded-lg hover:bg-error/10">
                <Trash2 size={14} />
              </button>
            )}
          </div>
        ),
      });
    }
    return cols;
  }, [initialColumns, onEdit, onDelete]);

  const table = useReactTable({
    data, columns,
    state: { globalFilter },
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 15 } },
  });

  return (
    <Card className="p-0 overflow-hidden flex flex-col h-full min-h-[400px] border-border/50">
      {loading ? (
        <div className="flex flex-col items-center justify-center h-64 space-y-3">
          <div className="w-10 h-10 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
          <div className="text-primary font-mono text-xs tracking-widest animate-pulse">LOADING DATA...</div>
        </div>
      ) : (
        <div className="w-full flex-1 flex flex-col min-h-0">
          <div className="overflow-auto flex-1">
            <table className="w-full text-sm text-left">
              <thead className="text-[10px] text-textMuted uppercase bg-surface border-b border-border sticky top-0 z-10">
                {table.getHeaderGroups().map(hg => (
                  <tr key={hg.id}>
                    {hg.headers.map(header => (
                      <th key={header.id} onClick={header.column.getToggleSortingHandler()}
                        className="px-5 py-3.5 cursor-pointer hover:text-primary transition-colors select-none group whitespace-nowrap tracking-wider">
                        <div className="flex items-center space-x-1.5">
                          <span>{flexRender(header.column.columnDef.header, header.getContext())}</span>
                          <span className="opacity-0 group-hover:opacity-100 transition-opacity">
                            {{ asc: <ChevronUp size={12} />, desc: <ChevronDown size={12} /> }
                              [header.column.getIsSorted()] ?? <ChevronDown size={12} className="text-textMuted/20" />}
                          </span>
                        </div>
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody className="divide-y divide-border/30">
                {table.getRowModel().rows.map((row, i) => (
                  <motion.tr key={row.id}
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    transition={{ delay: Math.min(i * 0.02, 0.3) }}
                    className="group hover:bg-primary/[0.03] transition-colors">
                    {row.getVisibleCells().map(cell => (
                      <td key={cell.id} className="px-5 py-3 whitespace-nowrap">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </motion.tr>
                ))}
                {table.getRowModel().rows.length === 0 && (
                  <tr>
                    <td colSpan={columns.length} className="px-6 py-16 text-center text-textMuted font-mono text-sm">
                      {noDataMessage}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between px-5 py-3 border-t border-border bg-surface/50 shrink-0">
            <div className="flex items-center space-x-3">
              <span className="text-[10px] text-textMuted font-mono hidden sm:block">
                {table.getFilteredRowModel().rows.length} records
                {globalFilter && ` (filtered from ${data.length})`}
              </span>

              {/* Page size */}
              <select value={table.getState().pagination.pageSize}
                onChange={e => table.setPageSize(Number(e.target.value))}
                className="bg-surface border border-border rounded text-[10px] font-mono text-textMuted px-2 py-1 focus:outline-none focus:border-primary">
                {[10, 15, 25, 50].map(s => <option key={s} value={s}>{s} / page</option>)}
              </select>

              {/* Export */}
              {onExport && (
                <div className="relative">
                  <Button variant="ghost" size="sm" onClick={() => setExportOpen(!exportOpen)}
                    className="flex items-center space-x-1.5 text-[10px] font-mono text-textMuted hover:text-primary border border-border hover:border-primary/40 px-2.5 py-1.5">
                    <Download size={12} /><span>EXPORT</span>
                  </Button>
                  {exportOpen && (
                    <div className="absolute bottom-full left-0 mb-1 bg-surface border border-border rounded-lg shadow-xl overflow-hidden min-w-[130px] z-50">
                      {[['pdf', 'PDF Report'], ['xlsx', 'Excel'], ['csv', 'CSV'], ['txt', 'Text']].map(([fmt, label]) => (
                        <button key={fmt} onClick={() => { onExport(fmt); setExportOpen(false); }}
                          className="block w-full px-4 py-2 text-xs font-mono text-textMain hover:bg-primary/10 hover:text-primary text-left transition-colors">
                          {label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Pagination */}
            <div className="flex items-center space-x-1">
              <Button variant="ghost" size="sm" onClick={() => table.setPageIndex(0)} disabled={!table.getCanPreviousPage()} className="p-1.5">
                <ChevronsLeft size={14} />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()} className="p-1.5">
                <ChevronLeft size={14} />
              </Button>
              <span className="px-3 text-[10px] font-mono font-bold text-primary tabular-nums">
                {table.getState().pagination.pageIndex + 1} / {table.getPageCount() || 1}
              </span>
              <Button variant="ghost" size="sm" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()} className="p-1.5">
                <ChevronRight size={14} />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => table.setPageIndex(table.getPageCount() - 1)} disabled={!table.getCanNextPage()} className="p-1.5">
                <ChevronsRight size={14} />
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
