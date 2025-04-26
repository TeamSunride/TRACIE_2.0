//import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';

export default {
  root: ".",          // Vite starts looking from inside OpenLayerMap
  publicDir: "public",
  base: "./",
  build: {
    sourcemap: false,
    input: "./index.html",  // HTML entry point
},
    outDir: "./dist",  // Output directory (bundled files)
    emptyOutDir: true,  // Clean dist/ before building
    plugins: [viteSingleFile()],
};

