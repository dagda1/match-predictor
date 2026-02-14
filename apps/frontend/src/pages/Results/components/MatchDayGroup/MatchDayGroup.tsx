import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import dayjs from 'dayjs';

import type { MatchResult } from '~/api/types';

import { MatchResultCard } from '../MatchResultCard/MatchResultCard';
import { sx } from './styles';

const DAY_HEADER_FORMAT = 'dddd D MMMM';

interface MatchDayGroupProps {
  date: string;
  matches: MatchResult[];
}

export function MatchDayGroup({ date, matches }: MatchDayGroupProps): JSX.Element {
  return (
    <Stack spacing={{ xs: 1.5, sm: 2 }}>
      <Typography variant="subtitle2" sx={sx.dayHeader}>
        {dayjs(date).format(DAY_HEADER_FORMAT)}
      </Typography>

      {matches.map((match) => (
        <MatchResultCard key={`${match.homeTeam}-${match.awayTeam}`} match={match} />
      ))}
    </Stack>
  );
}
