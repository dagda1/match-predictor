import checker from 'vite-plugin-checker';
import dts from 'vite-plugin-dts';
import { defineConfig } from 'vitest/config';

import { sharedTestConfig } from '../../vitest.shared';

const isDev = process.env.NODE_ENV === 'development';

process.env.NODE_ENV = process.env.NODE_ENV || 'production';

const entries = ['src/index.ts'];

export default defineConfig({
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  },
  plugins: [
    checker({ typescript: { tsconfigPath: 'tsconfig.dist.json' } }),
    dts({ tsconfigPath: 'tsconfig.dist.json', insertTypesEntry: true, logLevel: 'error' }),
  ],
  logLevel: 'warn',
  resolve: {
    tsconfigPaths: true,
  },
  build: {
    manifest: true,
    minify: true,
    outDir: './dist/esm',
    sourcemap: isDev ? 'inline' : false,
    lib: {
      entry: [...entries],
      formats: ['es'],
    },
    rolldownOptions: {
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
    environment: 'node',
  },
});
