import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';
import type { MatchResult } from '~/api/types';
import { ModelProbBars } from '~/pages/Home/components/ModelProbBars/ModelProbBars';
import { getModelColors } from '~/pages/Home/styles';
import { sx, cardSx, chipSx, mlColorSx, poissonColorSx } from './styles';

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

interface MatchResultCardProps {
  match: MatchResult;
}

export function MatchResultCard({ match }: MatchResultCardProps): JSX.Element {
  const theme = useTheme();
  const colors = getModelColors(theme.palette.mode);
  const bothCorrect = match.ml.correct && match.poisson.correct;
  const bothWrong = !match.ml.correct && !match.poisson.correct;

  return (
    <Paper sx={cardSx(bothCorrect, bothWrong)}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={sx.header}>
        <Typography variant="h6" sx={sx.score}>
          {match.homeTeam}{' '}
          <Box component="span" sx={sx.goals}>{match.actualHomeGoals}</Box>
          <Box component="span" sx={{ color: (t) => t.palette.text.disabled, fontWeight: 400, mx: 0.8, fontSize: '0.85em' }}>–</Box>
          <Box component="span" sx={sx.goals}>{match.actualAwayGoals}</Box>
          {' '}{match.awayTeam}
        </Typography>
        <Stack direction="row" spacing={1} sx={sx.chips}>
          <Chip label={`ML ${match.ml.correct ? '✓' : '✗'}`} size="small" sx={chipSx(match.ml.correct)} />
          <Chip label={`Poi ${match.poisson.correct ? '✓' : '✗'}`} size="small" sx={chipSx(match.poisson.correct)} />
        </Stack>
      </Stack>

      <Stack direction="row" spacing={{ xs: 2, sm: 3 }} sx={sx.predictedScores}>
        <Box>
          <Typography variant="caption" sx={sx.predictedLabel}>ML predicted</Typography>
          <Typography variant="body2" sx={{ ...sx.predictedValue as object, ...mlColorSx()(theme) }}>
            {match.ml.topScore.homeGoals}–{match.ml.topScore.awayGoals}{' '}
            <Box component="span" sx={sx.predictedProb}>{pct(match.ml.topScore.probability)}</Box>
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" sx={sx.predictedLabel}>Poisson predicted</Typography>
          <Typography variant="body2" sx={{ ...sx.predictedValue as object, ...poissonColorSx()(theme) }}>
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
