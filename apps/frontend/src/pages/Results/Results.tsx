import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import dayjs from 'dayjs';

import { ISO_DATE_FORMAT } from '~/constants';
import { useFetchResults } from '~/hooks/useFetchResults';

import { MatchResultCard } from './components/MatchResultCard/MatchResultCard';
import { sx } from './styles';

const today = dayjs();
const saturday = today.day() === 6 ? today : today.subtract(today.day() + 1, 'day');
const friday = saturday.add(6, 'day');

export function Results(): JSX.Element {
  const { data } = useFetchResults({
    startDate: saturday.format(ISO_DATE_FORMAT),
    endDate: friday.format(ISO_DATE_FORMAT),
  });

  return (
    <Container maxWidth="md" sx={sx.container}>
      <Stack spacing={{ xs: 2, sm: 3 }}>
        <Paper sx={sx.weekPicker}>
          <Box sx={sx.headerCenter}>
            <Typography variant="h5" sx={sx.weekTitle}>
              {saturday.format('D MMM')} – {friday.format('D MMM')}
            </Typography>
            <Typography variant="body2" sx={sx.weekDates}>
              {data.matches.length} matches
            </Typography>
          </Box>
        </Paper>

        <Paper sx={sx.summaryCard}>
          <Stack direction="row" spacing={{ xs: 2, sm: 4 }} justifyContent="center">
            <Box sx={sx.headerCenter}>
              <Typography variant="body2" sx={sx.summaryValue}>
                {data.summary.mlCorrect}/{data.summary.mlTotal}
              </Typography>
              <Typography variant="caption" sx={sx.summaryLabel}>
                ML correct
              </Typography>
            </Box>
            <Divider orientation="vertical" flexItem sx={sx.summaryDivider} />
            <Box sx={sx.headerCenter}>
              <Typography variant="body2" sx={sx.summaryValuePoisson}>
                {data.summary.poissonCorrect}/{data.summary.poissonTotal}
              </Typography>
              <Typography variant="caption" sx={sx.summaryLabel}>
                Poisson correct
              </Typography>
            </Box>
          </Stack>
        </Paper>

        {data.matches.map((match) => (
          <MatchResultCard key={`${match.homeTeam}-${match.awayTeam}`} match={match} />
        ))}
      </Stack>
    </Container>
  );
}

export default Results;
