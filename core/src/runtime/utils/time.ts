export function nowIso(): string {
  return new Date().toISOString();
}

export function nowMs(): number {
  return Date.now();
}

export function jobId(prefix: string = "job"): string {
  return `${prefix}-${nowMs()}`;
}

