import '../../../../types/mui.d.ts';

import { grey } from '@mui/material/colors';
import type { PaletteOptions } from '@mui/material/styles';

type Palettes = {
  light: PaletteOptions & { mode: 'light' };
  dark: PaletteOptions & { mode: 'dark' };
};

export const palettes: Palettes = {
  light: {
    mode: 'light',
    primary: {
      main: '#1B5E20',
    },
    secondary: {
      main: '#F5F5F5',
    },
    background: {
      default: '#FFFFFF',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1C1C1C',
      secondary: grey[700],
    },
  },
  dark: {
    mode: 'dark',
    primary: {
      main: '#66BB6A',
    },
    secondary: {
      main: '#303141',
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
    text: {
      primary: '#FFFFFF',
      secondary: grey[400],
    },
  },
};
