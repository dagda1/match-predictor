import { useCallback, useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import type { MatchweekDetail, MatchweekSummary } from '~/api/types';
import { fetchMatchweek, fetchMatchweeks } from '~/api/predict';
import { MatchResultCard } from './components/MatchResultCard/MatchResultCard';
import { sx } from './styles';

export function Results(): JSX.Element {
  const [weeks, setWeeks] = useState<MatchweekSummary[]>([]);
  const [weekIdx, setWeekIdx] = useState(0);
  const [detail, setDetail] = useState<MatchweekDetail | null>(null);

  useEffect(() => {
    fetchMatchweeks()
      .then((result) => {
        setWeeks(result);
        if (result.length > 0) {
          setWeekIdx(result.length - 1);
        }
      })
      .catch((error) => {
        console.error('failed to fetch matchweeks', error);
      });
  }, []);

  const loadWeek = useCallback((week: number) => {
    setDetail(null);
    fetchMatchweek(week)
      .then(setDetail)
      .catch((error) => {
        console.error('failed to fetch matchweek', { week }, error);
      });
  }, []);

  useEffect(() => {
    if (weeks.length > 0) {
      loadWeek(weeks[weekIdx].week);
    }
  }, [weekIdx, weeks, loadWeek]);

  if (weeks.length === 0) {
    return (
      <Container maxWidth="md" sx={sx.container}>
        <Paper sx={sx.emptyState}>
          <Typography variant="body1" sx={sx.emptyText}>
            No matchweek data available yet.
          </Typography>
        </Paper>
      </Container>
    );
  }

  const week = weeks[weekIdx];

  return (
    <Container maxWidth="md" sx={sx.container}>
      <Stack spacing={{ xs: 2, sm: 3 }}>
        <Paper sx={sx.weekPicker}>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <IconButton
              onClick={() => setWeekIdx(Math.max(0, weekIdx - 1))}
              disabled={weekIdx === 0}
              size="small"
              sx={sx.navButton}
            >
              <ChevronLeftIcon />
            </IconButton>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={sx.weekTitle}>
                Matchweek {week.week}
              </Typography>
              <Typography variant="body2" sx={sx.weekDates}>
                {week.startDate} – {week.endDate} · {week.matchCount} matches
              </Typography>
            </Box>
            <IconButton
              onClick={() => setWeekIdx(Math.min(weeks.length - 1, weekIdx + 1))}
              disabled={weekIdx === weeks.length - 1}
              size="small"
              sx={sx.navButton}
            >
              <ChevronRightIcon />
            </IconButton>
          </Stack>
        </Paper>

        {detail && (
          <>
            <Paper sx={sx.summaryCard}>
              <Stack direction="row" spacing={{ xs: 2, sm: 4 }} justifyContent="center">
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="body2" sx={sx.summaryValue}>
                    {detail.summary.mlCorrect}/{detail.summary.mlTotal}
                  </Typography>
                  <Typography variant="caption" sx={sx.summaryLabel}>ML correct</Typography>
                </Box>
                <Divider orientation="vertical" flexItem sx={sx.summaryDivider} />
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="body2" sx={sx.summaryValuePoisson}>
                    {detail.summary.poissonCorrect}/{detail.summary.poissonTotal}
                  </Typography>
                  <Typography variant="caption" sx={sx.summaryLabel}>Poisson correct</Typography>
                </Box>
              </Stack>
            </Paper>

            {detail.matches.map((match) => (
              <MatchResultCard key={`${match.homeTeam}-${match.awayTeam}`} match={match} />
            ))}
          </>
        )}
      </Stack>
    </Container>
  );
}

export default Results;
