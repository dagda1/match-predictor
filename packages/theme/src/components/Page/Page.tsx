import Box from '@mui/material/Box';
import { Outlet } from 'react-router';

import { TopNav } from '../TopNav/TopNav';
import { sx } from './styles';

export function Page(): JSX.Element {
  return (
    <Box sx={sx.root}>
      <TopNav />
      <Box component="main" sx={sx.main}>
        <Outlet />
      </Box>
    </Box>
  );
}
