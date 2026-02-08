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
import type { MatchweekDetail, MatchweekSummary, UpcomingResponse } from '~/api/types';
import { fetchMatchweek, fetchMatchweeks, fetchUpcoming } from '~/api/predict';
import { MatchResultCard } from './components/MatchResultCard/MatchResultCard';
import { UpcomingCard } from './components/UpcomingCard/UpcomingCard';
import { sx } from './styles';

export function Results(): JSX.Element {
  const [weeks, setWeeks] = useState<MatchweekSummary[]>([]);
  const [weekIdx, setWeekIdx] = useState(0);
  const [detail, setDetail] = useState<MatchweekDetail | null>(null);
  const [upcoming, setUpcoming] = useState<UpcomingResponse | null>(null);
  const [hasUpcoming, setHasUpcoming] = useState(false);

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

    fetchUpcoming()
      .then((result) => {
        if (result.matches.length > 0) {
          setUpcoming(result);
          setHasUpcoming(true);
        }
      })
      .catch((error) => {
        console.error('failed to fetch upcoming', error);
      });
  }, []);

  const totalPositions = weeks.length + (hasUpcoming ? 1 : 0);
  const isUpcomingSelected = hasUpcoming && weekIdx === weeks.length;

  const loadWeek = useCallback((week: number) => {
    setDetail(null);
    fetchMatchweek(week)
      .then(setDetail)
      .catch((error) => {
        console.error('failed to fetch matchweek', { week }, error);
      });
  }, []);

  useEffect(() => {
    if (weeks.length > 0 && weekIdx < weeks.length) {
      loadWeek(weeks[weekIdx].week);
    }
  }, [weekIdx, weeks, loadWeek]);

  if (weeks.length === 0 && !hasUpcoming) {
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
              {isUpcomingSelected && upcoming ? (
                <>
                  <Typography variant="h5" sx={sx.weekTitle}>
                    Upcoming
                  </Typography>
                  <Typography variant="body2" sx={sx.weekDates}>
                    {upcoming.startDate} – {upcoming.endDate} · {upcoming.matches.length} matches
                  </Typography>
                </>
              ) : weeks.length > 0 && weekIdx < weeks.length ? (
                <>
                  <Typography variant="h5" sx={sx.weekTitle}>
                    Matchweek {weeks[weekIdx].week}
                  </Typography>
                  <Typography variant="body2" sx={sx.weekDates}>
                    {weeks[weekIdx].startDate} – {weeks[weekIdx].endDate} · {weeks[weekIdx].matchCount} matches
                  </Typography>
                </>
              ) : null}
            </Box>
            <IconButton
              onClick={() => setWeekIdx(Math.min(totalPositions - 1, weekIdx + 1))}
              disabled={weekIdx === totalPositions - 1}
              size="small"
              sx={sx.navButton}
            >
              <ChevronRightIcon />
            </IconButton>
          </Stack>
        </Paper>

        {isUpcomingSelected && upcoming && (
          upcoming.matches.map((match) => (
            <UpcomingCard key={`${match.homeTeam}-${match.awayTeam}`} match={match} />
          ))
        )}

        {!isUpcomingSelected && detail && (
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
