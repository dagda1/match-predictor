import ContrastRoundedIcon from '@mui/icons-material/ContrastRounded';
import IconButton from '@mui/material/IconButton';

import { useThemeMode } from '../useThemeMode';

export function ThemeSwitcherIconButton(): JSX.Element {
  const { toggle } = useThemeMode();

  return (
    <IconButton onClick={toggle} aria-label="Toggle theme">
      <ContrastRoundedIcon />
    </IconButton>
  );
}
