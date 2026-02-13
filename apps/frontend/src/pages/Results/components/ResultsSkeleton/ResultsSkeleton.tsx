import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';
import Stack from '@mui/material/Stack';

import { sx } from './styles';

export function ResultsSkeleton(): JSX.Element {
  return (
    <Container maxWidth="md" sx={sx.container}>
      <Stack spacing={{ xs: 2, sm: 3 }}>
        <Paper sx={sx.header}>
          <Skeleton variant="text" width="40%" height={32} />
          <Skeleton variant="text" width="20%" height={18} />
        </Paper>

        <Paper sx={sx.summary}>
          <Stack direction="row" spacing={4} justifyContent="center">
            <Skeleton variant="text" width={60} height={28} />
            <Skeleton variant="text" width={60} height={28} />
          </Stack>
        </Paper>

        {Array.from({ length: 5 }, (_, index) => (
          <Paper key={index} sx={sx.matchCard}>
            <Skeleton variant="text" width="70%" height={28} />
            <Skeleton variant="text" width="50%" height={20} />
          </Paper>
        ))}
      </Stack>
    </Container>
  );
}
