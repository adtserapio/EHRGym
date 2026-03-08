import Link from "next/link";
import type { Route } from "next";

type AppBrandProps = {
  title: string;
  subtitle: string;
  href?: Route;
  compact?: boolean;
};

export function AppBrand({ title, subtitle, href = "/", compact = false }: AppBrandProps) {
  const content = (
    <>
      <span className={compact ? "app-brand__copy app-brand__copy--compact" : "app-brand__copy"}>
        <strong>{title}</strong>
        <span>{subtitle}</span>
      </span>
    </>
  );

  if (!href) {
    return <div className="app-brand">{content}</div>;
  }

  return (
    <Link href={href} className="app-brand" aria-label={title}>
      {content}
    </Link>
  );
}
