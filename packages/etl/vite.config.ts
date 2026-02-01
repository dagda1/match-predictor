import react from '@vitejs/plugin-react-swc';
import path from 'path';
import { fileURLToPath } from 'url';
import checker from 'vite-plugin-checker';
import dts from 'vite-plugin-dts';
import { nodePolyfills } from 'vite-plugin-node-polyfills';
import tsconfigPaths from 'vite-tsconfig-paths';
import { defineConfig } from 'vitest/config';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const isDev = process.env.NODE_ENV === 'development';

process.env.NODE_ENV = process.env.NODE_ENV || 'production';

const entries = ['src/index.ts'];

// https://vitejs.dev/config/
export default defineConfig({
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  },
  plugins: [
    checker({ typescript: { tsconfigPath: 'tsconfig.dist.json' } }),
    dts({ tsconfigPath: 'tsconfig.dist.json', insertTypesEntry: true, logLevel: 'error' }),
    nodePolyfills({
      globals: {
        Buffer: false,
        global: false,
        process: false,
      },
    }),
    tsconfigPaths(),
    react(),
  ],
  logLevel: 'warn',
  resolve: {
    dedupe: ['react', 'react-dom', '@emotion/react'],
  },
  optimizeDeps: {
    include: ['react/jsx-runtime', 'react', 'react-dom'],
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
    rollupOptions: {
      external: ['@emotion/styled', '@emotion/react', /^@mui\/.*/, 'react', 'react-dom'],
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
    globals: true,
    environment: 'jsdom',
    setupFiles: path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../setuptests.ts'),
    css: true,
    server: {
      deps: {
        fallbackCJS: true,
      },
    },
  },
});
