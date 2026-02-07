import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import { ThemeProvider } from '@match-predictor/theme';

import { appStyles } from './styles';

export function App(): JSX.Element {
  return (
    <ThemeProvider>
      <Container maxWidth="md" sx={appStyles.container}>
        <Typography variant="h4" component="h1">
          Match Predictor
        </Typography>
      </Container>
    </ThemeProvider>
  );
}
