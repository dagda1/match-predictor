import type { SxProps, Theme } from '@mui/material/styles';

import type { ModelVariant } from '../ModelProbBars/ModelProbBars';

function getChipColor(theme: Theme, variant: ModelVariant): string {
  return variant === 'ml' ? theme.palette.primary.main : theme.palette.warning.main;
}

function getChipAccentBg(theme: Theme, variant: ModelVariant): string {
  return variant === 'ml' ? theme.palette.primary.dark : theme.palette.warning.dark;
}

export const sx: Record<string, SxProps<Theme>> = {
  headCell: {
    fontWeight: 700,
    color: (theme: Theme) => theme.palette.text.secondary,
    fontSize: '0.7rem',
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
  },
  bodyRow: {
    '&:last-child td': { borderBottom: 0 },
  },
  rankCell: {
    fontWeight: 500,
    color: (theme: Theme) => theme.palette.text.secondary,
    width: 28,
  },
  score: {
    fontWeight: 600,
    fontFeatureSettings: "'tnum'",
    fontSize: '0.85rem',
  },
};

export function getChipSx(index: number, variant: ModelVariant): SxProps<Theme> {
  return (theme: Theme) => {
    const defaultBg = theme.palette.action.hover;
    const defaultColor = theme.palette.text.secondary;

    return {
      fontWeight: 600,
      fontFeatureSettings: "'tnum'",
      fontSize: '0.74rem',
      height: 24,
      bgcolor: index === 0 ? getChipColor(theme, variant) : index < 3 ? getChipAccentBg(theme, variant) : defaultBg,
      color:
        index === 0
          ? theme.palette.getContrastText(getChipColor(theme, variant))
          : index < 3
            ? theme.palette.getContrastText(getChipAccentBg(theme, variant))
            : defaultColor,
    };
  };
}
