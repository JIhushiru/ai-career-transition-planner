/**
 * Philippine peso salary formatting utilities.
 */

export function formatPHP(amount: number | null | undefined): string {
  if (amount == null) return "";
  return `PHP ${amount.toLocaleString()}`;
}

export function formatSalaryRange(
  min: number | null | undefined,
  max: number | null | undefined,
): string {
  if (min == null && max == null) return "";
  if (min != null && max != null && min !== max) {
    return `PHP ${min.toLocaleString()} - ${max.toLocaleString()}`;
  }
  return formatPHP(min ?? max);
}

export function formatSalaryDelta(delta: number | null | undefined): string {
  if (delta == null) return "";
  const sign = delta >= 0 ? "+" : "";
  return `${sign}PHP ${delta.toLocaleString()}`;
}
