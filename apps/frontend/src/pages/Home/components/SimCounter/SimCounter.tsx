import Typography from '@mui/material/Typography';
import { sx } from './styles';

interface SimCounterProps {
  count: number;
  total: number;
}

export function SimCounter({ count, total }: SimCounterProps): JSX.Element {
  return (
    <Typography variant="body2" sx={sx.counter}>
      {count.toLocaleString()} / {total.toLocaleString()} simulated
    </Typography>
  );
}
