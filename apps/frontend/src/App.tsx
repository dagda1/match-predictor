import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import { ThemeProvider, builtinThemes } from '@match-predictor/theme';

export function App(): JSX.Element {
  return (
    <ThemeProvider theme={builtinThemes.light}>
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1">
          Match Predictor
        </Typography>
      </Container>
    </ThemeProvider>
  );
}
