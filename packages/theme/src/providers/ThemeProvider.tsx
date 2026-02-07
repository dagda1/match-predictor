import CssBaseline from '@mui/material/CssBaseline';
import type { Theme } from '@mui/material/styles';
import { StyledEngineProvider } from '@mui/material/styles';
import MuiThemeProvider from '@mui/material/styles/ThemeProvider';
import type { ReactNode } from 'react';

import { GlobalStyles } from '../GlobalStyles';

export interface ThemeProviderProps {
  children: ReactNode;
  theme: Theme;
}

export function ThemeProvider(props: ThemeProviderProps): JSX.Element {
  const { children, theme } = props;

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
