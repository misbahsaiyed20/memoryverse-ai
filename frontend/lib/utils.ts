import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind classes conditionally. Used by shadcn/ui components
 * added in later sprints.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
