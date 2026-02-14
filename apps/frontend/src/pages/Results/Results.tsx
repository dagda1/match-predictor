import { assert } from '@cutting/assert';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import dayjs from 'dayjs';
import { useNavigate, useParams } from 'react-router';

import { DISPLAY_DATE_FORMAT, ISO_DATE_FORMAT, saturdayForDate } from '~/constants';
import { useFetchResults } from '~/hooks/useFetchResults';

import { MatchResultCard } from './components/MatchResultCard/MatchResultCard';
import { sx } from './styles';

export function Results(): JSX.Element {
  const { startDate, endDate } = useParams();
  const navigate = useNavigate();

  assert(!!startDate, 'startDate route param is required');
  assert(!!endDate, 'endDate route param is required');

  const { data } = useFetchResults({ startDate, endDate });

  const start = dayjs(startDate);
  const end = dayjs(endDate);

  function navigateToDate(matchDate: string) {
    const saturday = saturdayForDate(dayjs(matchDate));
    const friday = saturday.add(6, 'day');
    navigate(`/results/${saturday.format(ISO_DATE_FORMAT)}/${friday.format(ISO_DATE_FORMAT)}`);
  }

  return (
    <Container maxWidth="md" sx={sx.container}>
      <Stack spacing={{ xs: 2, sm: 3 }}>
        <Paper sx={sx.weekPicker}>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <IconButton
              disabled={!data.earlierMatchDate}
              onClick={() => navigateToDate(data.earlierMatchDate!)}
              size="small"
              sx={sx.navButton}
            >
              <ChevronLeftIcon />
            </IconButton>

            <Box sx={sx.headerCenter}>
              <Typography variant="h5" sx={sx.weekTitle}>
                {start.format(DISPLAY_DATE_FORMAT)} – {end.format(DISPLAY_DATE_FORMAT)}
              </Typography>
              <Typography variant="body2" sx={sx.weekDates}>
                {data.matches.length} matches
              </Typography>
            </Box>

            <IconButton
              disabled={!data.laterMatchDate}
              onClick={() => navigateToDate(data.laterMatchDate!)}
              size="small"
              sx={sx.navButton}
            >
              <ChevronRightIcon />
            </IconButton>
          </Stack>
        </Paper>

        {data.summary.mlTotal > 0 && (
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
        )}

        {data.matches.length === 0 ? (
          <Paper sx={sx.emptyState}>
            <Typography variant="body1" sx={sx.emptyText}>
              No matches this week
            </Typography>
          </Paper>
        ) : (
          data.matches.map((match) => <MatchResultCard key={`${match.homeTeam}-${match.awayTeam}`} match={match} />)
        )}
      </Stack>
    </Container>
  );
}

export default Results;
