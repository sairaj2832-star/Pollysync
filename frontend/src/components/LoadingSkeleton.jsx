export function Skeleton({ className = "" }) {
  return (
    <div className={`animate-pulse rounded-xl bg-surface-container-highest ${className}`} />
  );
}

export function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-12 gap-lg">
      <Skeleton className="col-span-12 md:col-span-4 h-64" />
      <Skeleton className="col-span-12 md:col-span-5 h-64" />
      <Skeleton className="col-span-12 md:col-span-3 h-64" />
      <Skeleton className="col-span-12 md:col-span-6 h-48" />
      <Skeleton className="col-span-12 md:col-span-6 h-48" />
      <Skeleton className="col-span-12 md:col-span-8 h-56" />
      <Skeleton className="col-span-12 md:col-span-4 h-56" />
      <Skeleton className="col-span-12 md:col-span-6 h-64" />
      <Skeleton className="col-span-12 md:col-span-6 h-64" />
      <Skeleton className="col-span-12 h-72" />
    </div>
  );
}
