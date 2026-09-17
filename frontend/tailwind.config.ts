import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        black: "#000000",
        coral: {
          DEFAULT: "#FF5733",
          hover: "#E04826",
          muted: "rgba(255, 87, 51, 0.15)",
        },
        cobalt: {
          DEFAULT: "#0047AB",
          hover: "#003A8C",
          muted: "rgba(0, 71, 171, 0.15)",
        },
        surface: {
          base: "#050505",
          elevated: "#0C0C0C",
          card: "#111111",
          border: "#1C1C1C",
        },
      },
      fontFamily: {
        sans: [
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          '"Segoe UI"',
          "Roboto",
          '"Helvetica Neue"',
          "sans-serif",
        ],
        heading: [
          '"Arial Black"',
          '"Impact"',
          "system-ui",
          "-apple-system",
          "sans-serif",
        ],
      },
      letterSpacing: {
        ultra: "0.18em",
        wide: "0.08em",
      },
    },
  },
  plugins: [],
};

export default config;
