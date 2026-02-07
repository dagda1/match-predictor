import DarkModeRoundedIcon from '@mui/icons-material/DarkModeRounded';
import LightModeRoundedIcon from '@mui/icons-material/LightModeRounded';
import IconButton from '@mui/material/IconButton';

import { useThemeMode } from '../useThemeMode';

export function ThemeSwitcherIconButton(): JSX.Element {
  const { mode, toggle } = useThemeMode();

  return (
    <IconButton onClick={toggle} aria-label="Toggle theme">
      {mode === 'dark' ? <LightModeRoundedIcon /> : <DarkModeRoundedIcon />}
    </IconButton>
  );
}
