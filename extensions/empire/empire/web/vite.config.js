import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5178,
    strictPort: true,
    proxy: {
      "/health": "http://127.0.0.1:8991",
      "/records": "http://127.0.0.1:8991",
      "/events": "http://127.0.0.1:8991",
      "/tasks": "http://127.0.0.1:8991"
    }
  }
});
