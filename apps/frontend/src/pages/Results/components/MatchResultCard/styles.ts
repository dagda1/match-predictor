import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  header: {
    mb: 1,
  },
  score: {
    fontSize: { xs: '1rem', sm: '1.15rem' },
    fontWeight: 700,
    lineHeight: 1.3,
  },
  goals: {
    fontWeight: 700,
    fontFeatureSettings: "'tnum'",
  },
  dash: {
    color: (theme: Theme) => theme.palette.text.disabled,
    fontWeight: 400,
    mx: 0.8,
    fontSize: '0.85em',
  },
  modelDivider: {
    borderColor: (theme: Theme) =>
      theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)',
    mx: 2,
    display: { xs: 'none', sm: 'block' },
  },
  predictedScores: {
    mb: { xs: 1.5, sm: 2 },
  },
  predictedLabel: {
    fontSize: '0.68rem',
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
    color: (theme: Theme) => theme.palette.text.secondary,
  },
  predictedValue: {
    fontWeight: 700,
    fontFeatureSettings: "'tnum'",
    fontSize: '0.88rem',
  },
  mlPredictedValue: {
    fontWeight: 700,
    fontFeatureSettings: "'tnum'",
    fontSize: '0.88rem',
    color: (theme: Theme) => theme.palette.primary.main,
  },
  poissonPredictedValue: {
    fontWeight: 700,
    fontFeatureSettings: "'tnum'",
    fontSize: '0.88rem',
    color: (theme: Theme) => theme.palette.warning.main,
  },
  predictedProb: {
    fontWeight: 500,
    fontSize: '0.78rem',
    color: (theme: Theme) => theme.palette.text.secondary,
  },
};

export function cardSx(bothCorrect: boolean, bothWrong: boolean): SxProps<Theme> {
  return (theme: Theme) => {
    const successColor = theme.palette.success.main;
    const errorColor = theme.palette.error.main;
    const borderColor = bothCorrect
      ? `${successColor}66`
      : bothWrong
        ? `${errorColor}44`
        : theme.palette.divider;
    const bgTint = bothCorrect
      ? `${successColor}08`
      : bothWrong
        ? `${errorColor}06`
        : 'transparent';

    return {
      px: { xs: 2, sm: 3 },
      py: { xs: 2, sm: 2.5 },
      border: `1px solid ${borderColor}`,
      bgcolor: bgTint,
    };
  };
}

