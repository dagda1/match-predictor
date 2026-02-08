import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';
import type { UpcomingMatch } from '~/api/types';
import { ModelProbBars } from '~/pages/Home/components/ModelProbBars/ModelProbBars';
import { getModelColors } from '~/pages/Home/styles';
import { sx, mlColorSx, poissonColorSx } from './styles';

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
}

interface UpcomingCardProps {
  match: UpcomingMatch;
}

export function UpcomingCard({ match }: UpcomingCardProps): JSX.Element {
  const theme = useTheme();
  const colors = getModelColors(theme.palette.mode);

  return (
    <Paper sx={sx.card}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={sx.header}>
        <Box>
          <Typography variant="h6" sx={sx.teams}>
            {match.homeTeam}
            <Box component="span" sx={{ color: (t) => t.palette.text.disabled, fontWeight: 400, mx: 0.8, fontSize: '0.85em' }}>vs</Box>
            {match.awayTeam}
          </Typography>
          <Typography variant="body2" sx={sx.date}>
            {formatDate(match.date)}
          </Typography>
        </Box>
      </Stack>

      <Stack direction="row" spacing={{ xs: 2, sm: 3 }} sx={sx.predictedScores}>
        <Box>
          <Typography variant="caption" sx={sx.predictedLabel}>ML predicted</Typography>
          <Typography variant="body2" sx={{ ...sx.predictedValue as object, ...mlColorSx(theme) }}>
            {match.ml.topScore.homeGoals}–{match.ml.topScore.awayGoals}{' '}
            <Box component="span" sx={sx.predictedProb}>{pct(match.ml.topScore.probability)}</Box>
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" sx={sx.predictedLabel}>Poisson predicted</Typography>
          <Typography variant="body2" sx={{ ...sx.predictedValue as object, ...poissonColorSx(theme) }}>
            {match.poisson.topScore.homeGoals}–{match.poisson.topScore.awayGoals}{' '}
            <Box component="span" sx={sx.predictedProb}>{pct(match.poisson.topScore.probability)}</Box>
          </Typography>
        </Box>
      </Stack>

      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={0}
        divider={
          <Divider
            orientation="vertical"
            flexItem
            sx={{ borderColor: (t) => t.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)', mx: 2, display: { xs: 'none', sm: 'block' } }}
          />
        }
      >
        <ModelProbBars
          title="ML Model"
          subtitle={null}
          homeWin={match.ml.homeWin}
          draw={match.ml.draw}
          awayWin={match.ml.awayWin}
          home={match.homeTeam}
          away={match.awayTeam}
          animProbs={null}
          isSimulating={false}
          colors={colors.ml}
          compact={true}
        />
        <ModelProbBars
          title="Poisson Baseline"
          subtitle={null}
          homeWin={match.poisson.homeWin}
          draw={match.poisson.draw}
          awayWin={match.poisson.awayWin}
          home={match.homeTeam}
          away={match.awayTeam}
          animProbs={null}
          isSimulating={false}
          colors={colors.poisson}
          compact={true}
        />
      </Stack>
    </Paper>
  );
}
