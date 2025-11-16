import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

if (process.env.VITE_API_PROTOCOL) {
  console.log('Vite config - VITE_API_PROTOCOL:', process.env.VITE_API_PROTOCOL)
}
if (process.env.VITE_API_IP) {
  console.log('Vite config - VITE_API_IP:', process.env.VITE_API_IP)
}

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
    minify: 'esbuild' as const,
    target: 'es2015',
    cssMinify: true,
    sourcemap: false,
    reportCompressedSize: false,
    rollupOptions: {
      maxParallelFileOps: 2,
    },
  },
})
