import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FAFAF9",
        surface: "#FFFFFF",
        foreground: "#14141A",
        muted: "#6B6B76",
        border: "#E7E7EC",
        accent: {
          DEFAULT: "#5B4FE8",
          foreground: "#FFFFFF",
          soft: "#EFEDFD",
        },
        trust: {
          DEFAULT: "#0F9D6E",
          soft: "#E7F7F0",
        },
      },
      boxShadow: {
        card: "0 1px 2px rgba(20, 20, 26, 0.04), 0 8px 24px -12px rgba(20, 20, 26, 0.10)",
      },
      fontFamily: {
        // System font stack — no external font requests, and this *is*
        // Apple's own San Francisco on macOS/iOS, which suits the brief.
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Inter",
          "sans-serif",
        ],
        display: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Inter",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};

export default config;
