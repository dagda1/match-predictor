import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  container: {
    py: { xs: 1, sm: 2 },
  },
  card: {
    px: { xs: 2.5, sm: 4 },
    py: { xs: 2.5, sm: 4 },
  },
  title: {
    mb: 0.3,
    fontSize: { xs: '1.25rem', sm: '1.5rem' },
  },
  subtitle: {
    mb: { xs: 2, sm: 3 },
  },
  teamStack: {
    mb: { xs: 2, sm: 3 },
  },
  predictButton: (theme: Theme) => ({
    py: { xs: 1.2, sm: 1.4 },
    fontSize: { xs: '0.9rem', sm: '1rem' },
    background: theme.palette.mode === 'dark'
      ? 'linear-gradient(135deg, #5B2D8E 0%, #7C4DFF 100%)'
      : 'linear-gradient(135deg, #3D195B 0%, #5B2D8E 100%)',
    '&:hover': {
      background: theme.palette.mode === 'dark'
        ? 'linear-gradient(135deg, #4A2375 0%, #6A3DE0 100%)'
        : 'linear-gradient(135deg, #2E1245 0%, #4A2375 100%)',
    },
  }),
  predictButtonDisabled: {
    py: { xs: 1.2, sm: 1.4 },
    fontSize: { xs: '0.9rem', sm: '1rem' },
  },
  newPredButton: {
    py: { xs: 1, sm: 1.2 },
  },
  progressContainer: {
    mb: 2,
  },
  progressBar: (theme: Theme) => ({
    height: 6,
    borderRadius: 3,
    bgcolor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : theme.palette.grey[200],
    '& .MuiLinearProgress-bar': {
      borderRadius: 3,
      background: theme.palette.mode === 'dark'
        ? 'linear-gradient(90deg, #7C4DFF 0%, #00FF87 100%)'
        : 'linear-gradient(90deg, #3D195B 0%, #00FF87 100%)',
    },
  }),
  predictionHeader: {
    textAlign: 'center',
    mb: { xs: 2, sm: 3 },
  },
  predictionLabel: (theme: Theme) => ({
    color: theme.palette.text.secondary,
    fontWeight: 500,
    mb: 0.3,
    fontSize: '0.75rem',
  }),
  predictionTeams: {
    fontSize: { xs: '1.05rem', sm: '1.35rem' },
    lineHeight: 1.3,
  },
  vsText: (theme: Theme) => ({
    color: theme.palette.mode === 'dark' ? theme.palette.grey[700] : theme.palette.grey[400],
    fontWeight: 400,
    mx: 0.5,
  }),
  divider: (theme: Theme) => ({
    borderColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)',
    my: 2,
  }),
  dividerVertical: (theme: Theme) => ({
    borderColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)',
    mx: 2.5,
  }),
  scoreSubtitle: {
    mb: 1,
  },
  mlTab: (theme: Theme) => ({
    color: theme.palette.text.secondary,
    fontSize: { xs: '0.8rem', sm: '0.85rem' },
    '&.Mui-selected': {
      color: theme.palette.mode === 'dark' ? '#b09aff' : '#3D195B',
    },
  }),
  poissonTab: (theme: Theme) => ({
    color: theme.palette.text.secondary,
    fontSize: { xs: '0.8rem', sm: '0.85rem' },
    '&.Mui-selected': {
      color: theme.palette.mode === 'dark' ? '#ffab40' : '#E65100',
    },
  }),
};

export function tabsIndicatorSx(selectedTab: number): SxProps<Theme> {
  return (theme: Theme) => ({
    mb: 1.5,
    '& .MuiTabs-indicator': {
      backgroundColor: selectedTab === 0
        ? (theme.palette.mode === 'dark' ? '#7C4DFF' : '#3D195B')
        : (theme.palette.mode === 'dark' ? '#FF6D00' : '#E65100'),
    },
  });
}

interface ModelColorSet {
  homeWin: string;
  draw: string;
  awayWin: string;
  chip: string;
  chipAccentBg: string;
  chipAccentText: string;
}

export interface ModelColors {
  ml: ModelColorSet;
  poisson: ModelColorSet;
}

export function getModelColors(mode: 'light' | 'dark'): ModelColors {
  const isDark = mode === 'dark';
  return {
    ml: {
      homeWin: isDark ? '#7C4DFF' : '#3D195B',
      draw: isDark ? '#546E7A' : '#78909C',
      awayWin: '#00E676',
      chip: isDark ? '#7C4DFF' : '#3D195B',
      chipAccentBg: isDark ? 'rgba(124,77,255,0.15)' : '#ede7f6',
      chipAccentText: isDark ? '#b09aff' : '#3D195B',
    },
    poisson: {
      homeWin: isDark ? '#FF6D00' : '#E65100',
      draw: isDark ? '#546E7A' : '#78909C',
      awayWin: isDark ? '#26C6DA' : '#00838F',
      chip: isDark ? '#FF6D00' : '#E65100',
      chipAccentBg: isDark ? 'rgba(255,109,0,0.15)' : '#fff3e0',
      chipAccentText: isDark ? '#ffab40' : '#E65100',
    },
  };
}
