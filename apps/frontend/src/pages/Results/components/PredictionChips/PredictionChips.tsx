import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';

import { chipSx, sx } from './styles';

interface PredictionChipsProps {
  mlCorrect: boolean;
  poissonCorrect: boolean;
}

function labelFor(correct: boolean): string {
  return correct ? '✓' : '✗';
}

export function PredictionChips({ mlCorrect, poissonCorrect }: Readonly<PredictionChipsProps>): JSX.Element {
  return (
    <Stack direction="row" spacing={1} sx={sx.chips}>
      <Chip label={`ML ${labelFor(mlCorrect)}`} size="small" sx={chipSx(mlCorrect)} />
      <Chip label={`Poi ${labelFor(poissonCorrect)}`} size="small" sx={chipSx(poissonCorrect)} />
    </Stack>
  );
}
