import Box from '@mui/material/Box';
import { Outlet } from 'react-router';

import { TopNav } from './TopNav';
import { pageStyles } from './styles';

export function Page(): JSX.Element {
  return (
    <Box sx={pageStyles.root}>
      <TopNav />
      <Box component="main" sx={pageStyles.main}>
        <Outlet />
      </Box>
    </Box>
  );
}
