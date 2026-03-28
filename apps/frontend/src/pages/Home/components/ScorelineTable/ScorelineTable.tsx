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

import type { ModelVariant } from '../ModelProbBars/ModelProbBars';
import { getChipSx, sx } from './styles';

interface Props {
  scorelines: Scoreline[];
  revealed: number | null;
  variant: ModelVariant;
}

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function ScorelineTable({ scorelines, revealed, variant }: Readonly<Props>): JSX.Element {
  const rows = revealed !== null ? scorelines.slice(0, revealed) : scorelines;

  return (
    <TableContainer>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={sx.headCell}>#</TableCell>
            <TableCell sx={sx.headCell}>Score</TableCell>
            <TableCell align="right" sx={sx.headCell}>
              Prob
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((scoreline, index) => (
            <Grow in key={`${scoreline.homeGoals}-${scoreline.awayGoals}`} timeout={300 + index * 80}>
              <TableRow sx={sx.bodyRow}>
                <TableCell sx={sx.rankCell}>{index + 1}</TableCell>
                <TableCell>
                  <Typography variant="body2" sx={sx.score}>
                    {scoreline.homeGoals} – {scoreline.awayGoals}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Chip label={pct(scoreline.probability)} size="small" sx={getChipSx(index, variant)} />
                </TableCell>
              </TableRow>
            </Grow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
