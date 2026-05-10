/**
 * TeleTrack — Response Data Extractor
 * Safely extracts array data from backend responses which may be:
 * - Paginated: { success: true, data: [...], meta: {...} }
 * - Direct: { success: true, data: {...} }
 * - Array of items in data
 */
export function extractItems(response) {
  if (!response || !response.success) return [];
  const d = response.data;
  if (Array.isArray(d)) return d;
  if (d && Array.isArray(d.items)) return d.items;
  return [];
}

export function extractSingle(response) {
  if (!response || !response.success) return null;
  return response.data || null;
}
