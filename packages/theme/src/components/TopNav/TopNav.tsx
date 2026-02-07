import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';

import { MaxWidthContainer } from '../MaxWidthContainer/MaxWidthContainer';
import { ThemeSwitcherIconButton } from '../ThemeSwitcherIconButton';
import { sx } from './styles';

export function TopNav(): JSX.Element {
  return (
    <AppBar position="static" color="default" elevation={1}>
      <MaxWidthContainer>
        <Toolbar>
          <Typography variant="h6" sx={sx.title}>
            Match Predictor
          </Typography>
          <ThemeSwitcherIconButton />
        </Toolbar>
      </MaxWidthContainer>
    </AppBar>
  );
}
