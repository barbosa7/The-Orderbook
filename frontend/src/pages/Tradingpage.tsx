import { useState, useEffect } from 'react';
import { Container, Grid, Paper, Title, Group, Select } from '@mantine/core';
import { OrderBook } from '../components/OrderBook';
import { OrderEntry } from '../components/OrderEntry';
import { TradeHistory } from '../components/TradeHistory';
import { PnLDisplay } from '../components/PnLDisplay';
import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';
import { Leaderboard } from '../components/Leaderboard';

export const TradingPage = () => {
  const { isAuthenticated, user } = useAuth();
  const [activeSymbol, setActiveSymbol] = useState('AAPL');
  const competitionId = 'default_competition';

  useEffect(() => {
    console.log("TradingPage - Auth state:", { isAuthenticated, user });
  }, [isAuthenticated, user]);

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" />;
  }

  return (
    <Container size="xl" py="xl">
      <Group position="apart" mb="xl">
        <Title order={2}>Trading Dashboard</Title>
        <Select
          value={activeSymbol}
          onChange={(value) => setActiveSymbol(value || 'AAPL')}
          data={[
            { value: 'AAPL', label: 'Apple Inc.' },
            { value: 'GOOGL', label: 'Google' },
          ]}
          style={{ width: 200 }}
        />
      </Group>

      <Grid>
        <Grid.Col span={8}>
          {user && <PnLDisplay competitionId={competitionId} />}
          <Paper mt="md">
            <OrderBook 
              competitionId={competitionId} 
              symbol={activeSymbol} 
            />
          </Paper>
        </Grid.Col>
        <Grid.Col span={4}>
          <Paper mt="md">
            <Leaderboard competitionId={competitionId} />
          </Paper>
          <Paper mt="md">
            <TradeHistory 
              competitionId={competitionId}
              symbol={activeSymbol}
            />
          </Paper>
        </Grid.Col>
      </Grid>
    </Container>
  );
}; 