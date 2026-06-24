import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium leading-none",
  {
    variants: {
      tone: {
        good: "border-[#bbf7d0] bg-[#ecfdf3] text-[#067647]",
        warn: "border-[#fedf89] bg-[#fffaeb] text-[#b54708]",
        danger: "border-[#fecdca] bg-[#fef3f2] text-[#b42318]",
        neutral: "border-workbench-border bg-workbench-panel2 text-workbench-muted"
      }
    },
    defaultVariants: {
      tone: "neutral"
    }
  }
);

export interface BadgeProps extends VariantProps<typeof badgeVariants> {
  className?: string;
  children: React.ReactNode;
}

export function Badge({ className, tone, children }: BadgeProps) {
  return <span className={cn(badgeVariants({ tone, className }))}>{children}</span>;
}
