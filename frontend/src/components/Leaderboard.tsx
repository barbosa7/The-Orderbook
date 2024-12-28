import { useEffect, useState } from 'react';
import { Paper, Table, Text, Skeleton } from '@mantine/core';
import { api } from '../services/api';

interface LeaderboardEntry {
  user_id: string;
  total_pnl: number;
  rank: number;
}

interface Props {
  competitionId: string;
}

export const Leaderboard: React.FC<Props> = ({ competitionId }) => {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const { data } = await api.get(`/competition/${competitionId}/leaderboard`);
        const validatedData = data.map((entry: any) => ({
          user_id: entry.user_id || 'Unknown',
          total_pnl: typeof entry.total_pnl === 'number' ? entry.total_pnl : 0,
          rank: entry.rank || 0
        }));
        setEntries(validatedData);
        setError(null);
      } catch (error) {
        console.error('Failed to fetch leaderboard:', error);
        setError('Failed to fetch leaderboard');
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
    const interval = setInterval(fetchLeaderboard, 1000);
    return () => clearInterval(interval);
  }, [competitionId]);

  if (loading) return <Paper p="md"><Skeleton height={200} /></Paper>;
  if (error) return <Paper p="md"><Text color="red">{error}</Text></Paper>;

  return (
    <Paper p="md">
      <Text size="xl" weight={700} mb="md">Leaderboard</Text>
      <Table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Trader</th>
            <th style={{ textAlign: 'right' }}>P&L</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.user_id}>
              <td>{entry.rank}</td>
              <td>{entry.user_id}</td>
              <td style={{ 
                textAlign: 'right',
                color: entry.total_pnl >= 0 ? 'green' : 'red' 
              }}>
                ${entry.total_pnl.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Paper>
  );
};
