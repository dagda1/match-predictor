import type { SxProps, Theme } from '@mui/material/styles';

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

export function chipSx(
  index: number,
  chipColor: string,
  chipAccentBg: string,
  chipAccentText: string,
): SxProps<Theme> {
  return (theme: Theme) => {
    const defaultBg = theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : theme.palette.grey[100];
    const defaultColor = theme.palette.text.secondary;

    return {
      fontWeight: 600,
      fontFeatureSettings: "'tnum'",
      fontSize: '0.74rem',
      height: 24,
      bgcolor: index === 0 ? chipColor : index < 3 ? chipAccentBg : defaultBg,
      color: index === 0 ? '#fff' : index < 3 ? chipAccentText : defaultColor,
    };
  };
}
