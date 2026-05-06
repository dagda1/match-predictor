import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import type { MatchResult } from '~/api/types';
import { ModelProbBars } from '~/pages/Home/components/ModelProbBars/ModelProbBars';

import { PredictionChips } from '../PredictionChips/PredictionChips';
import { cardSx, sx } from './styles';

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

interface MatchResultCardProps {
  match: MatchResult;
}

export function MatchResultCard({ match }: Readonly<MatchResultCardProps>): JSX.Element {
  const bothCorrect = match.played && match.ml.correct && match.poisson.correct;
  const bothWrong = match.played && !match.ml.correct && !match.poisson.correct;

  return (
    <Paper sx={cardSx(bothCorrect, bothWrong)}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={sx.header}>
        {match.played ? (
          <Typography variant="h6" sx={sx.score}>
            {match.homeTeam}{' '}
            <Box component="span" sx={sx.goals}>
              {match.actualHomeGoals}
            </Box>
            <Box component="span" sx={sx.dash}>
              –
            </Box>
            <Box component="span" sx={sx.goals}>
              {match.actualAwayGoals}
            </Box>{' '}
            {match.awayTeam}
          </Typography>
        ) : (
          <Typography variant="h6" sx={sx.score}>
            {match.homeTeam} vs {match.awayTeam}
          </Typography>
        )}

        {match.played && (
          <PredictionChips mlCorrect={match.ml.correct} poissonCorrect={match.poisson.correct} />
        )}
      </Stack>

      <Stack direction="row" spacing={{ xs: 2, sm: 3 }} sx={sx.predictedScores}>
        <Box>
          <Typography variant="caption" sx={sx.predictedLabel}>
            ML predicted
          </Typography>
          <Typography variant="body2" sx={sx.mlPredictedValue}>
            {match.ml.topScore.homeGoals}–{match.ml.topScore.awayGoals}{' '}
            <Box component="span" sx={sx.predictedProb}>
              {pct(match.ml.topScore.probability)}
            </Box>
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" sx={sx.predictedLabel}>
            Poisson predicted
          </Typography>
          <Typography variant="body2" sx={sx.poissonPredictedValue}>
            {match.poisson.topScore.homeGoals}–{match.poisson.topScore.awayGoals}{' '}
            <Box component="span" sx={sx.predictedProb}>
              {pct(match.poisson.topScore.probability)}
            </Box>
          </Typography>
        </Box>
      </Stack>

      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={0}
        divider={<Divider orientation="vertical" flexItem sx={sx.modelDivider} />}
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
          variant="ml"
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
          variant="poisson"
          compact={true}
        />
      </Stack>
    </Paper>
  );
}
