import { describe, it, expect } from 'vitest';

import { builtinThemes } from './builtinThemes';

describe('builtinThemes', () => {
  it('creates light and dark themes with correct palette modes', () => {
    expect(builtinThemes.light.palette.mode).toBe('light');
    expect(builtinThemes.dark.palette.mode).toBe('dark');
  });
});
