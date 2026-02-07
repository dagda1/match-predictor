import path from 'path';
import { fileURLToPath } from 'url';
import { defineConfig } from 'vitest/config';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const config = defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    css: false,
    setupFiles: path.resolve(__dirname, 'setupTests.ts'),
    server: {
      deps: {
        fallbackCJS: true,
      },
    },
  },
});

export const sharedTestConfig = config.test!;
