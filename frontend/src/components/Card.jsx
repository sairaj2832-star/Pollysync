/**
 * Reusable Card component with header, content, and footer slots
 * Provides consistent styling across the app
 */
export default function Card({
  children,
  header,
  badge,
  footer,
  className = "",
  variant = "default",
}) {
  const baseStyles =
    "bg-surface border border-outline-variant rounded-xl p-lg shadow-[0_1px_3px_rgba(0,0,0,0.05)]";

  const variantStyles = {
    default: baseStyles,
    elevated: baseStyles + " shadow-[0_3px_8px_rgba(0,0,0,0.12)]",
    filled: baseStyles + " bg-surface-container-lowest",
    compact: baseStyles + " p-md",
  };

  return (
    <div className={`${variantStyles[variant] || variantStyles.default} ${className}`}>
      {/* Header with optional badge */}
      {header && (
        <div className="flex justify-between items-start mb-md">
          {typeof header === "string" ? (
            <h3 className="font-headline-sm text-headline-sm text-on-surface">{header}</h3>
          ) : (
            header
          )}
          {badge && <div>{badge}</div>}
        </div>
      )}

      {/* Main content */}
      {typeof children === "string" ? (
        <p className="font-body-md text-body-md text-on-surface-variant">{children}</p>
      ) : (
        children
      )}

      {/* Footer */}
      {footer && <div className="mt-lg pt-md border-t border-outline-variant/50">{footer}</div>}
    </div>
  );
}
