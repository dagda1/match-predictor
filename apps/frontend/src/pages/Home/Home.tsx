import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';

import { sx } from './styles';

export function Home(): JSX.Element {
  return (
    <Container maxWidth="md" sx={sx.container}>
      <Typography variant="h4" component="h1">
        Match Predictor
      </Typography>
    </Container>
  );
}

export default Home;
