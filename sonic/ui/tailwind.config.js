/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{svelte,js,ts}"] ,
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#05060b",
          900: "#0b0f1a",
          800: "#141a2a",
          700: "#1e2538"
        },
        neon: {
          blue: "#5cc8ff",
          green: "#46f0b3",
          pink: "#ff5fd6"
        }
      },
      fontFamily: {
        display: ["Space Grotesk", "IBM Plex Sans", "sans-serif"],
        mono: ["IBM Plex Mono", "JetBrains Mono", "monospace"]
      },
      boxShadow: {
        glow: "0 0 30px rgba(92, 200, 255, 0.18)"
      }
    }
  },
  plugins: []
};
