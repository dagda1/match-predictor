import AppBar from '@mui/material/AppBar';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { NavLink } from 'react-router';

import { MaxWidthContainer } from '../MaxWidthContainer/MaxWidthContainer';
import { ThemeSwitcherIconButton } from '../ThemeSwitcherIconButton';
import { sx, navLinkSx } from './styles';

export interface NavLinkItem {
  label: string;
  to: string;
}

interface TopNavProps {
  navLinks?: NavLinkItem[];
}

export function TopNav({ navLinks = [] }: TopNavProps): JSX.Element {
  return (
    <AppBar position="static" color="default" elevation={1}>
      <MaxWidthContainer>
        <Toolbar>
          <Typography variant="h6" sx={sx.title}>
            Match Predictor
          </Typography>
          {navLinks.length > 0 && (
            <Stack direction="row" spacing={0.5} sx={sx.navLinks}>
              {navLinks.map((link) => (
                <Button
                  key={link.to}
                  component={NavLink}
                  to={link.to}
                  size="small"
                  sx={navLinkSx}
                >
                  {link.label}
                </Button>
              ))}
            </Stack>
          )}
          <ThemeSwitcherIconButton />
        </Toolbar>
      </MaxWidthContainer>
    </AppBar>
  );
}
