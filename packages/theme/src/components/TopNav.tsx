import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';

import { ThemeSwitcherIconButton } from './ThemeSwitcherIconButton';
import { topNavStyles } from './styles';

export function TopNav(): JSX.Element {
  return (
    <AppBar position="static" color="default" elevation={1}>
      <Toolbar>
        <Typography variant="h6" sx={topNavStyles.title}>
          Match Predictor
        </Typography>
        <ThemeSwitcherIconButton />
      </Toolbar>
    </AppBar>
  );
}
