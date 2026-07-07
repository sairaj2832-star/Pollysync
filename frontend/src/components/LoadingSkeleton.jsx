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

export function EmptyState({
  icon = "inbox",
  title = "No data",
  description = "There's nothing here yet",
  action,
  actionLabel = "Get Started",
}) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="text-center max-w-sm">
        <span className="material-symbols-outlined text-6xl text-on-surface-variant mb-md block">
          {icon}
        </span>
        <h3 className="font-headline-md text-headline-md text-on-surface mb-sm">{title}</h3>
        <p className="font-body-md text-body-md text-on-surface-variant mb-lg">{description}</p>
        {action && (
          <button
            onClick={action}
            className="px-lg py-sm rounded-lg bg-primary text-on-primary font-label-md text-label-md font-bold hover:bg-primary/90 transition"
          >
            {actionLabel}
          </button>
        )}
      </div>
    </div>
  );
}

export function ErrorState({
  error = "Something went wrong",
  onRetry,
  retryLabel = "Retry",
}) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="text-center max-w-sm">
        <span className="material-symbols-outlined text-6xl text-tertiary mb-md block">error</span>
        <h3 className="font-headline-md text-headline-md text-on-surface mb-sm">Error</h3>
        <p className="font-body-md text-body-md text-on-surface-variant mb-lg">{error}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-lg py-sm rounded-lg bg-tertiary text-on-error font-label-md text-label-md font-bold hover:bg-tertiary/90 transition"
          >
            {retryLabel}
          </button>
        )}
      </div>
    </div>
  );
}
