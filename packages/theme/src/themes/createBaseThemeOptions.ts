import type { PaletteOptions } from '@mui/material/styles';
import type { TypographyOptions } from '@mui/material/styles/createTypography';
import deepmerge from '@mui/utils/deepmerge';

import { DEFAULT_FONT_FAMILY, DEFAULT_HTML_FONT_SIZE } from '../constants';

export interface BaseThemeOptions {
  palette: PaletteOptions;
  fontFamily?: string;
  htmlFontSize?: number;
  typography?: TypographyOptions;
}

export function createBaseThemeOptions(options: BaseThemeOptions): {
  palette: PaletteOptions;
  typography: TypographyOptions;
} {
  const { palette, htmlFontSize = DEFAULT_HTML_FONT_SIZE, fontFamily = DEFAULT_FONT_FAMILY, typography } = options;

  const defaultTypography: TypographyOptions = {
    htmlFontSize,
    fontFamily,
    h1: { fontSize: 54, fontWeight: 400 },
    h2: { fontSize: 40, fontWeight: 400 },
    h3: { fontSize: 32, fontWeight: 400 },
    h4: { fontSize: 28, fontWeight: 400 },
    h5: { fontSize: 24, fontWeight: 400 },
    h6: { fontSize: 18, fontWeight: 400 },
    fontWeightRegular: 400,
  };

  return {
    palette,
    typography: deepmerge(defaultTypography, typography),
  };
}
