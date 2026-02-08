import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { ProbBar } from '../ProbBar/ProbBar';
import { sx } from './styles';

interface AnimProbs {
  h: number;
  d: number;
  a: number;
}

interface ModelColors {
  homeWin: string;
  draw: string;
  awayWin: string;
}

interface ModelProbBarsProps {
  title: string;
  subtitle: string | null;
  homeWin: number;
  draw: number;
  awayWin: number;
  home: string | null;
  away: string | null;
  animProbs: AnimProbs | null;
  isSimulating: boolean;
  colors: ModelColors;
  compact: boolean;
}

export function ModelProbBars({
  title,
  subtitle,
  homeWin,
  draw,
  awayWin,
  home,
  away,
  animProbs,
  isSimulating,
  colors,
  compact,
}: ModelProbBarsProps): JSX.Element {
  return (
    <Box sx={sx.root}>
      <Typography variant="subtitle2" sx={compact ? sx.titleCompact : sx.title}>
        {title}
      </Typography>
      {subtitle && (
        <Typography variant="caption" sx={sx.subtitle}>
          {subtitle}
        </Typography>
      )}
      {!subtitle && <Box sx={compact ? sx.spacerCompact : sx.spacer} />}
      <ProbBar
        label={`${home ?? 'Home'} win`}
        value={homeWin}
        animatedValue={isSimulating && animProbs ? animProbs.h : null}
        color={colors.homeWin}
        compact={compact}
      />
      <ProbBar
        label="Draw"
        value={draw}
        animatedValue={isSimulating && animProbs ? animProbs.d : null}
        color={colors.draw}
        compact={compact}
      />
      <ProbBar
        label={`${away ?? 'Away'} win`}
        value={awayWin}
        animatedValue={isSimulating && animProbs ? animProbs.a : null}
        color={colors.awayWin}
        compact={compact}
      />
    </Box>
  );
}
