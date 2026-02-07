import react from '@vitejs/plugin-react-swc';
import checker from 'vite-plugin-checker';
import dts from 'vite-plugin-dts';
import tsconfigPaths from 'vite-tsconfig-paths';
import { defineConfig } from 'vitest/config';

import { sharedTestConfig } from '../../vitest.shared';

const isDev = process.env.NODE_ENV === 'development';
const isProd = process.env.NODE_ENV === 'production';
process.env.NODE_ENV = process.env.NODE_ENV || 'production';

const entries = ['src/index.ts'];

export default defineConfig({
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  },
  plugins: [
    checker({ typescript: { tsconfigPath: 'tsconfig.dist.json' } }),
    dts({ tsconfigPath: 'tsconfig.dist.json', insertTypesEntry: true, logLevel: 'error' }),
    tsconfigPaths(),
    react(),
  ],
  logLevel: 'warn',
  resolve: {
    dedupe: ['react', 'react-dom', '@emotion/react'],
  },
  build: {
    manifest: true,
    minify: true,
    outDir: './dist/esm',
    sourcemap: isProd ? false : 'inline',
    lib: {
      entry: [...entries],
      formats: ['es'],
    },
    rollupOptions: {
      external: ['@emotion/styled', '@emotion/react', /^@mui\/.*/, 'react', 'react-dom', 'react-router'],
      input: [...entries],
      output: {
        preserveModulesRoot: 'src',
        preserveModules: true,
        dir: 'dist/esm',
        format: 'esm',
      },
    },
  },
  test: {
    ...sharedTestConfig,
  },
});
