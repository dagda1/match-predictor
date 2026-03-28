import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

import { ProbBar } from '../ProbBar/ProbBar';
import { sx } from './styles';

interface AnimProbs {
  h: number;
  d: number;
  a: number;
}

export type ModelVariant = 'ml' | 'poisson';

interface Props {
  title: string;
  subtitle: string | null;
  homeWin: number;
  draw: number;
  awayWin: number;
  home: string | null;
  away: string | null;
  animProbs: AnimProbs | null;
  isSimulating: boolean;
  variant: ModelVariant;
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
  variant,
  compact,
}: Readonly<Props>): JSX.Element {
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
        outcome="homeWin"
        variant={variant}
        compact={compact}
      />
      <ProbBar
        label="Draw"
        value={draw}
        animatedValue={isSimulating && animProbs ? animProbs.d : null}
        outcome="draw"
        variant={variant}
        compact={compact}
      />
      <ProbBar
        label={`${away ?? 'Away'} win`}
        value={awayWin}
        animatedValue={isSimulating && animProbs ? animProbs.a : null}
        outcome="awayWin"
        variant={variant}
        compact={compact}
      />
    </Box>
  );
}
