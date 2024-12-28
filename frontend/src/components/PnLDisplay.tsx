import { useEffect, useState } from 'react';
import { Paper, Text, Group, Divider, Skeleton } from '@mantine/core';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface Position {
  quantity: number;
  average_price: number;
  market_value: number;
}

interface ParticipantData {
  id: string;
  username: string;
  cash: number;
  positions: {
    [symbol: string]: Position;
  };
}

interface Props {
  competitionId: string;
}

export const PnLDisplay: React.FC<Props> = ({ competitionId }) => {
  const { user } = useAuth();
  const [participantData, setParticipantData] = useState<ParticipantData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!user) return;
      
      try {
        const { data } = await api.get(`/competition/${competitionId}/participant/${user.id}`);
        setParticipantData(data);
        setError(null);
      } catch (error: any) {
        setError('Failed to fetch participant data');
        console.error('Failed to fetch participant data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, [competitionId, user]);

  if (!user) return null;
  if (loading) return <Paper p="md"><Skeleton height={60} /></Paper>;
  if (error) return <Paper p="md"><Text color="red">{error}</Text></Paper>;
  if (!participantData) return <Paper p="md"><Text>No participant data found</Text></Paper>;

  const totalPnL = participantData.cash - 1000000; // Initial cash is 1,000,000

  return (
    <Paper p="md">
      <Group position="apart">
        <Text size="xl" weight={700}>Total P&L</Text>
        <Text 
          size="xl" 
          weight={700} 
          color={totalPnL >= 0 ? 'green' : 'red'}
        >
          ${totalPnL.toFixed(2)}
        </Text>
      </Group>
      <Divider my="sm" />
      <Group position="apart">
        <Text>Cash Balance:</Text>
        <Text>${participantData.cash.toFixed(2)}</Text>
      </Group>
      {Object.entries(participantData.positions || {}).map(([symbol, position]) => (
        <Group key={symbol} position="apart">
          <Text>{symbol}:</Text>
          <Text>{position.quantity} @ ${position.average_price.toFixed(2)}</Text>
        </Group>
      ))}
    </Paper>
  );
};
