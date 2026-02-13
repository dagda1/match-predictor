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
  chips: {
    flexShrink: 0,
    ml: 1.5,
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
  predictedProb: {
    fontWeight: 500,
    fontSize: '0.78rem',
    color: (theme: Theme) => theme.palette.text.secondary,
  },
};

export function cardSx(bothCorrect: boolean, bothWrong: boolean): (theme: Theme) => Record<string, unknown> {
  return (theme: Theme) => {
    const isDark = theme.palette.mode === 'dark';
    const borderColor = bothCorrect
      ? (isDark ? 'rgba(0,230,118,0.3)' : 'rgba(0,200,83,0.4)')
      : bothWrong
        ? (isDark ? 'rgba(255,82,82,0.25)' : 'rgba(255,82,82,0.3)')
        : (isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)');
    const bgTint = bothCorrect
      ? (isDark ? 'rgba(0,230,118,0.03)' : 'rgba(0,200,83,0.03)')
      : bothWrong
        ? (isDark ? 'rgba(255,82,82,0.03)' : 'rgba(255,82,82,0.02)')
        : 'transparent';
    return {
      px: { xs: 2, sm: 3 },
      py: { xs: 2, sm: 2.5 },
      border: `1px solid ${borderColor}`,
      bgcolor: bgTint,
    };
  };
}

export function chipSx(correct: boolean): (theme: Theme) => Record<string, unknown> {
  return (theme: Theme) => {
    const isDark = theme.palette.mode === 'dark';
    return {
      fontWeight: 700,
      fontSize: '0.72rem',
      height: 24,
      bgcolor: correct
        ? (isDark ? 'rgba(0,230,118,0.12)' : 'rgba(0,200,83,0.12)')
        : (isDark ? 'rgba(255,82,82,0.12)' : 'rgba(255,82,82,0.1)'),
      color: correct ? '#00E676' : (isDark ? '#FF5252' : '#D32F2F'),
      border: 'none',
    };
  };
}

export function mlColorSx(): (theme: Theme) => Record<string, unknown> {
  return (theme: Theme) => ({
    color: theme.palette.mode === 'dark' ? '#b09aff' : '#3D195B',
  });
}

export function poissonColorSx(): (theme: Theme) => Record<string, unknown> {
  return (theme: Theme) => ({
    color: theme.palette.mode === 'dark' ? '#ffab40' : '#E65100',
  });
}
