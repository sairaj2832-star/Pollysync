/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        leaf: {
          50: "#f0fdf4",
          500: "#22c55e",
          700: "#15803d",
          950: "#052e16"
        },
        pollen: "#f59e0b"
      },
      boxShadow: {
        soft: "0 18px 50px -24px rgba(5, 46, 22, 0.35)"
      }
    }
  },
  plugins: []
};
