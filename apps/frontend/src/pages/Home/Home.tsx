import Alert from '@mui/material/Alert';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';

import { ScorelineResults } from './components/ScorelineResults/ScorelineResults';
import { SimulationResults } from './components/SimulationResults/SimulationResults';
import { TeamSelectionCard } from './components/TeamSelectionCard/TeamSelectionCard';
import { useMatchPrediction } from './hooks/useMatchPrediction';
import { sx } from './styles';

export function Home(): JSX.Element {
  const {
    teams,
    teamsLoading,
    teamsError,
    home,
    away,
    phase,
    prediction,
    simProgress,
    mlAnimProbs,
    poissonAnimProbs,
    revealedRows,
    setHome,
    setAway,
    handlePredict,
    handleReset,
  } = useMatchPrediction();

  const isSimulating = phase === 'simulating';
  const showResults = (isSimulating || phase === 'result') && prediction !== null;

  return (
    <Container maxWidth="md" sx={sx.container}>
      <Stack spacing={{ xs: 2, sm: 3 }}>
        {teamsError && (
          <Alert severity="error">
            Failed to load teams: {teamsError.message}
          </Alert>
        )}
        <TeamSelectionCard
          home={home}
          away={away}
          teams={teams}
          teamsLoading={teamsLoading}
          phase={phase}
          onHomeChange={setHome}
          onAwayChange={setAway}
          onPredict={handlePredict}
          onReset={handleReset}
        />

        {showResults && prediction && (
          <SimulationResults
            prediction={prediction}
            home={home}
            away={away}
            isSimulating={isSimulating}
            isResult={phase === 'result'}
            simProgress={simProgress}
            mlAnimProbs={mlAnimProbs}
            poissonAnimProbs={poissonAnimProbs}
          />
        )}

        {showResults && prediction && (
          <ScorelineResults prediction={prediction} isSimulating={isSimulating} revealedRows={revealedRows} />
        )}
      </Stack>
    </Container>
  );
}

export default Home;
