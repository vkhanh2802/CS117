/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "Roboto", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        mint: {
          50: "#ecfdf7",
          100: "#d1faec",
          500: "#14b8a6",
          600: "#0d9488",
        },
        skysoft: {
          50: "#eff8ff",
          100: "#dbeafe",
          500: "#38bdf8",
          600: "#0284c7",
        },
      },
      boxShadow: {
        soft: "0 18px 40px rgba(15, 23, 42, 0.08)",
      },
    },
  },
  plugins: [],
};
