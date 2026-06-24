import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Segoe UI", "Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Cascadia Mono", "Consolas", "monospace"]
      },
      colors: {
        workbench: {
          base: "#f5f7fb",
          panel: "#ffffff",
          panel2: "#f1f5f9",
          border: "#d7dee8",
          text: "#101828",
          muted: "#667085",
          amber: "#c78517",
          teal: "#2457c5",
          red: "#b42318",
          violet: "#7c3aed"
        }
      },
      boxShadow: {
        panel: "0 18px 44px rgba(15, 23, 42, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
