import react from '@vitejs/plugin-react-swc';
import checker from 'vite-plugin-checker';
import tsconfigPaths from 'vite-tsconfig-paths';
import { defineConfig } from 'vitest/config';

import { sharedTestConfig } from '../../vitest.shared';

const isProd = process.env.NODE_ENV === 'production';

process.env.NODE_ENV = process.env.NODE_ENV || 'production';

export default defineConfig({
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  },
  plugins: [
    checker({ typescript: { tsconfigPath: 'tsconfig.dist.json' } }),
    tsconfigPaths(),
    react(),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  logLevel: 'warn',
  resolve: {
    dedupe: ['react', 'react-dom', '@emotion/react', '@mui/material'],
  },
  optimizeDeps: {
    include: ['react/jsx-runtime', 'react', 'react-dom'],
  },
  build: {
    sourcemap: isProd ? false : 'inline',
    minify: isProd,
    rollupOptions: {
      output: {
        format: 'esm',
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router'],
          'vendor-mui': [
            '@mui/material',
            '@emotion/react',
            '@emotion/styled',
          ],
          'vendor-utils': ['recharts'],
        },
      },
    },
  },
  test: {
    ...sharedTestConfig,
  },
});
