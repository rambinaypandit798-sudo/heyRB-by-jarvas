import icon from "@/assets/rb-agent-icon.png";
import { cn } from "@/lib/utils";

export function BrandMark({ size = 40, className }: { size?: number; className?: string }) {
  return (
    <img
      src={icon}
      alt="RB Agent"
      width={size}
      height={size}
      className={cn("shrink-0 select-none drop-shadow-sm", className)}
      style={{ width: size, height: size }}
    />
  );
}
