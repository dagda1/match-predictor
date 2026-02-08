import Chip from '@mui/material/Chip';
import Grow from '@mui/material/Grow';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import type { Scoreline } from '~/api/types';
import { sx, chipSx } from './styles';

interface ScorelineTableProps {
  scorelines: Scoreline[];
  revealed: number | null;
  chipColor: string;
  chipAccentBg: string;
  chipAccentText: string;
}

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

export function ScorelineTable({
  scorelines,
  revealed,
  chipColor,
  chipAccentBg,
  chipAccentText,
}: ScorelineTableProps): JSX.Element {
  const rows = revealed != null ? scorelines.slice(0, revealed) : scorelines;

  return (
    <TableContainer>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={sx.headCell}>#</TableCell>
            <TableCell sx={sx.headCell}>Score</TableCell>
            <TableCell align="right" sx={sx.headCell}>Prob</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((s, i) => (
            <Grow in key={`${s.homeGoals}-${s.awayGoals}`} timeout={300 + i * 80}>
              <TableRow sx={sx.bodyRow}>
                <TableCell sx={sx.rankCell}>{i + 1}</TableCell>
                <TableCell>
                  <Typography variant="body2" sx={sx.score}>
                    {s.homeGoals} – {s.awayGoals}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Chip
                    label={pct(s.probability)}
                    size="small"
                    sx={chipSx(i, chipColor, chipAccentBg, chipAccentText)}
                  />
                </TableCell>
              </TableRow>
            </Grow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
