import { defineConfig, loadEnv } from "vite";

import path from "path";
import react from "@vitejs/plugin-react";
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const isProduction = mode === "production";
  const isAnalyze = mode === "analyze";

  return {
    plugins: [
      react(),
      isAnalyze &&
        visualizer({
          open: true,
          filename: "dist/stats.html",
          gzipSize: true,
          brotliSize: true,
        }),
    ].filter(Boolean),
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      proxy: {
        "/api": {
          target: env.VITE_BASE_URL,
          changeOrigin: true,
        },
      },
    },
    build: {
      target: "esnext",
      minify: "terser",
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true,
          pure_funcs: [
            "console.log",
            "console.info",
            "console.debug",
            "console.trace",
          ],
        },
        mangle: true,
        format: {
          comments: false,
        },
      },
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ["react", "react-dom", "react-router-dom"],
            "ui-core": [
              "@radix-ui/react-slot",
              "@radix-ui/react-label",
              "class-variance-authority",
              "clsx",
              "tailwind-merge",
            ],
            "ui-components": [
              "@radix-ui/react-accordion",
              "@radix-ui/react-avatar",
              "@radix-ui/react-collapsible",
              "@radix-ui/react-dialog",
              "@radix-ui/react-dropdown-menu",
              "@radix-ui/react-hover-card",
              "@radix-ui/react-icons",
              "@radix-ui/react-menubar",
              "@radix-ui/react-navigation-menu",
              "@radix-ui/react-popover",
              "@radix-ui/react-progress",
              "@radix-ui/react-slider",
              "@radix-ui/react-switch",
              "@radix-ui/react-tabs",
              "@radix-ui/react-toast",
              "@radix-ui/react-tooltip",
            ],
            phaser: ["phaser"],
            "matter-js": ["matter-js"],
            utils: ["axios", "js-cookie"],
            docx: ["docx"],
            icons: ["lucide-react"],
          },
          chunkFileNames: isProduction
            ? "assets/[name]-[hash].js"
            : "assets/[name].js",
          entryFileNames: isProduction
            ? "assets/[name]-[hash].js"
            : "assets/[name].js",
          assetFileNames: isProduction
            ? "assets/[name]-[hash].[ext]"
            : "assets/[name].[ext]",
        },
      },
      chunkSizeWarningLimit: 500,
      sourcemap: false,
      cssCodeSplit: true,
      reportCompressedSize: false,
      emptyOutDir: true,
      assetsInlineLimit: 4096,
      modulePreload: false,
      cssMinify: true,
    },
  };
});
