import { createAppTheme } from './createTheme';
import { palettes } from './palettes';

export const builtinThemes = {
  light: createAppTheme({ palette: palettes.light }),
  dark: createAppTheme({ palette: palettes.dark }),
};
