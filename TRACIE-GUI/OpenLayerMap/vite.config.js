import { defineConfig } from 'vite';

export default defineConfig({
  root: ".",          // Vite starts looking from inside OpenLayerMap
  publicDir: "public",
  base: "./",
  build: {
    rollupOptions: {
      input: "./index.html",  // HTML entry point
    },
    outDir: "./dist",  // Output directory (bundled files)
    emptyOutDir: true,  // Clean dist/ before building
  },
});

