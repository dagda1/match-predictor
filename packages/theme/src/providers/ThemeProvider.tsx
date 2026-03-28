import CssBaseline from '@mui/material/CssBaseline';
import { StyledEngineProvider } from '@mui/material/styles';
import { ThemeProvider as MuiThemeProvider} from '@mui/material/styles';
import type { ReactNode } from 'react';

import { GlobalStyles } from '../GlobalStyles';
import { builtinThemes } from '../themes/builtinThemes';
import { useThemeMode } from '../useThemeMode';

export interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps): JSX.Element {
  const { mode } = useThemeMode();
  const theme = builtinThemes[mode];

  return (
    <StyledEngineProvider injectFirst>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        <GlobalStyles />
        {children}
      </MuiThemeProvider>
    </StyledEngineProvider>
  );
}
