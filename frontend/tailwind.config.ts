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
