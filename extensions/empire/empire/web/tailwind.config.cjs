module.exports = {
  content: ["./index.html", "./src/**/*.{svelte,js,ts}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Space Grotesk", "ui-sans-serif", "system-ui", "sans-serif"],
        body: ["IBM Plex Sans", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "SFMono-Regular", "monospace"]
      },
      colors: {
        empire: {
          50: "#fef6e7",
          100: "#fde9c7",
          200: "#fbd48b",
          300: "#f7b857",
          400: "#f29a2f",
          500: "#e77f18",
          600: "#c65b10",
          700: "#9b4011",
          800: "#7b3213",
          900: "#652b13"
        }
      },
      boxShadow: {
        glow: "0 0 40px rgba(242, 154, 47, 0.25)"
      }
    }
  },
  plugins: []
};
