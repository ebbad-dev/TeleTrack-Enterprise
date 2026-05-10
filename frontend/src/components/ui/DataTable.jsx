import React from 'react';
import { motion } from 'framer-motion';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
} from '@tanstack/react-table';
import { ChevronDown, ChevronUp, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Edit, Trash2, Download } from 'lucide-react';
import { Card } from './Card';
import { Button } from './Button';

export function DataTable({ columns: initialColumns, data, loading, globalFilter, setGlobalFilter, searchPlaceholder = "Search...", noDataMessage = "NO RESULTS FOUND", onEdit, onDelete, onExport, exportLabel = "Export CSV" }) {
  
  const columns = React.useMemo(() => {
    let cols = [...initialColumns];
    if (onEdit || onDelete) {
      cols.push({
        id: 'actions',
        header: 'Actions',
        cell: (info) => (
          <div className="flex items-center space-x-2">
            {onEdit && (
              <button onClick={() => onEdit(info.row.original)} className="p-1.5 text-textMuted hover:text-primary transition-colors rounded hover:bg-primary/10">
                <Edit size={14} />
              </button>
            )}
            {onDelete && (
              <button onClick={() => onDelete(info.row.original.id || info.row.original.device_id)} className="p-1.5 text-textMuted hover:text-error transition-colors rounded hover:bg-error/10">
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
    data,
    columns,
    state: { globalFilter },
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.05 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -10 },
    show: { opacity: 1, x: 0 }
  };

  return (
    <Card className="p-0 overflow-hidden flex flex-col h-full min-h-[400px]">
      {loading ? (
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          <div className="text-primary font-mono text-sm tracking-widest animate-pulse">FETCHING DATABANKS...</div>
        </div>
      ) : (
        <div className="w-full flex-1 flex flex-col">
          <div className="overflow-x-auto flex-1">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-textMuted uppercase bg-surfaceHighlight border-b border-border sticky top-0 z-10">
                {table.getHeaderGroups().map(headerGroup => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map(header => (
                      <th 
                        key={header.id} 
                        onClick={header.column.getToggleSortingHandler()}
                        className="px-6 py-4 cursor-pointer hover:text-primary transition-colors select-none group whitespace-nowrap"
                      >
                        <div className="flex items-center space-x-1">
                          <span>{flexRender(header.column.columnDef.header, header.getContext())}</span>
                          <span className="opacity-0 group-hover:opacity-100 transition-opacity">
                            {{
                              asc: <ChevronUp size={14} />,
                              desc: <ChevronDown size={14} />,
                            }[header.column.getIsSorted()] ?? <ChevronDown size={14} className="text-textMuted/30" />}
                          </span>
                        </div>
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <motion.tbody 
                variants={containerVariants}
                initial="hidden"
                animate="show"
                className="divide-y divide-border/50"
              >
                {table.getRowModel().rows.map(row => (
                  <motion.tr 
                    key={row.id} 
                    variants={itemVariants}
                    className="group hover:bg-surfaceHighlight/30 transition-colors"
                  >
                    {row.getVisibleCells().map(cell => (
                      <td key={cell.id} className="px-6 py-3 whitespace-nowrap">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </motion.tr>
                ))}
                {table.getRowModel().rows.length === 0 && (
                  <tr>
                    <td colSpan={columns.length} className="px-6 py-12 text-center text-textMuted font-mono text-lg">
                      {noDataMessage}
                    </td>
                  </tr>
                )}
              </motion.tbody>
            </table>
          </div>
          
          {/* Pagination + Export Controls */}
          <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-surfaceHighlight/20 shrink-0">
            <div className="flex items-center space-x-3">
              <div className="text-xs text-textMuted font-mono hidden sm:block">
                Showing {table.getRowModel().rows.length} of {data.length} entries
              </div>
              {onExport && (
                <div className="relative group">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    className="flex items-center space-x-1.5 text-xs font-mono text-textMuted hover:text-primary border border-border hover:border-primary/50"
                  >
                    <Download size={14} />
                    <span>EXPORT</span>
                  </Button>
                  <div className="absolute bottom-full left-0 mb-2 hidden group-hover:flex flex-col bg-surfaceHighlight border border-border rounded-md shadow-lg overflow-hidden min-w-[120px]">
                    <button onClick={() => onExport('pdf')} className="px-4 py-2 text-xs font-mono text-textMain hover:bg-primary/20 text-left transition-colors">PDF Report</button>
                    <button onClick={() => onExport('xlsx')} className="px-4 py-2 text-xs font-mono text-textMain hover:bg-primary/20 text-left transition-colors">Excel (XLSX)</button>
                    <button onClick={() => onExport('csv')} className="px-4 py-2 text-xs font-mono text-textMain hover:bg-primary/20 text-left transition-colors">CSV Data</button>
                    <button onClick={() => onExport('txt')} className="px-4 py-2 text-xs font-mono text-textMain hover:bg-primary/20 text-left transition-colors">Notepad (TXT)</button>
                  </div>
                </div>
              )}
            </div>
            <div className="flex space-x-2">
              <Button variant="ghost" size="sm" onClick={() => table.setPageIndex(0)} disabled={!table.getCanPreviousPage()}>
                <ChevronsLeft size={16} />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>
                <ChevronLeft size={16} />
              </Button>
              <span className="flex items-center px-4 text-xs font-mono font-bold text-primary">
                {table.getState().pagination.pageIndex + 1} / {table.getPageCount()}
              </span>
              <Button variant="ghost" size="sm" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
                <ChevronRight size={16} />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => table.setPageIndex(table.getPageCount() - 1)} disabled={!table.getCanNextPage()}>
                <ChevronsRight size={16} />
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
