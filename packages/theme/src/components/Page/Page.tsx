import Box from '@mui/material/Box';
import { Outlet } from 'react-router';

import { MaxWidthContainer } from '../MaxWidthContainer/MaxWidthContainer';
import type { NavLinkItem } from '../TopNav/TopNav';
import { TopNav } from '../TopNav/TopNav';
import { sx } from './styles';

interface PageProps {
  navLinks?: NavLinkItem[];
}

export function Page({ navLinks }: PageProps): JSX.Element {
  return (
    <Box sx={sx.root}>
      <TopNav navLinks={navLinks} />
      <Box component="main" sx={sx.main}>
        <MaxWidthContainer>
          <Outlet />
        </MaxWidthContainer>
      </Box>
    </Box>
  );
}
