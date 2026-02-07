import type { Theme } from '@mui/material/styles';
import createMuiTheme from '@mui/material/styles/createTheme';

import type { BaseThemeOptions } from './createBaseThemeOptions';
import { createBaseThemeOptions } from './createBaseThemeOptions';

export function createAppTheme(options: BaseThemeOptions): Theme {
  const themeOptions = createBaseThemeOptions(options);

  return createMuiTheme({
    palette: themeOptions.palette,
    typography: themeOptions.typography,
    components: {
      MuiCssBaseline: {
        styleOverrides: (themeParam) => ({
          'input:-webkit-autofill, textarea:-webkit-autofill, select:-webkit-autofill': {
            WebkitBoxShadow: `0 0 0 1000px ${themeParam.palette.background.paper} inset !important`,
            WebkitTextFillColor: `${themeParam.palette.text.primary} !important`,
            caretColor: `${themeParam.palette.text.primary} !important`,
            borderRadius: 'inherit',
          },
        }),
      },
    },
  });
}
