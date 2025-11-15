import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@app': path.resolve(__dirname, './src/app'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@widgets': path.resolve(__dirname, './src/widgets'),
      '@features': path.resolve(__dirname, './src/features'),
      '@entities': path.resolve(__dirname, './src/entities'),
      '@shared': path.resolve(__dirname, './src/shared'),
    },
  },
  build: {
    chunkSizeWarningLimit: 1000,
    minify: 'esbuild',
    target: 'es2015',
    cssMinify: true,
    sourcemap: false,
    reportCompressedSize: false,
    rollupOptions: {
      maxParallelFileOps: 2,
      output: {
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react-vendor';
            }
            if (id.includes('atomic-router')) {
              return 'router-vendor';
            }
            if (id.includes('@excalidraw') || id.includes('swagger-ui') || id.includes('mermaid')) {
              return 'ui-vendor';
            }
            return 'vendor';
          }
        },
      },
    },
  },
})
