import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';
import checker from 'vite-plugin-checker';
import { defineConfig } from 'vitest/config';

import { sharedTestConfig } from '../../vitest.shared';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const isDev = process.env.NODE_ENV === 'development';
const isTest = process.env.NODE_ENV === 'test';
const isProd = process.env.NODE_ENV === 'production';
const isCI = process.env.CI === 'true';

process.env.NODE_ENV = process.env.NODE_ENV || 'production';

const addAlias = (isDev || isTest) && !isCI;

const alias = {
  ...(addAlias && {
    '@match-predictor/theme': path.resolve(__dirname, '../../packages/theme/src'),
  }),
};

export default defineConfig({
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  },
  plugins: [
    checker({ typescript: { tsconfigPath: 'tsconfig.dist.json' } }),
    react(),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:4400',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api/, ''),
      },
    },
  },
  logLevel: 'warn',
  resolve: {
    dedupe: ['react', 'react-dom', '@emotion/react', '@mui/material'],
    alias,
    tsconfigPaths: true
  },
  optimizeDeps: {
    include: ['react/jsx-runtime', 'react', 'react-dom'],
  },
  build: {
    sourcemap: isProd ? false : 'inline',
    minify: isProd,
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            { name: 'vendor-react', test: /react|react-dom|react-router/, priority: 20 },
            { name: 'vendor-mui', test: /@mui|@emotion/, priority: 15 },
            { name: 'vendor-utils', test: /recharts/, priority: 10 },
          ],
        },
      },
    },
  },
  test: {
    ...sharedTestConfig,
  },
});
