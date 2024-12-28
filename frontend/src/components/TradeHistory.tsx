import { useEffect, useState } from 'react';
import { Paper, Table, Text } from '@mantine/core';
import { api } from '../services/api';
import { Trade } from '../types';

interface Props {
  competitionId: string;
  symbol: string;
}

interface TradeWithUsernames extends Trade {
  buyer_name: string;
  seller_name: string;
}

export const TradeHistory: React.FC<Props> = ({ competitionId, symbol }) => {
  const [trades, setTrades] = useState<TradeWithUsernames[]>([]);
  const [usernames, setUsernames] = useState<{[key: string]: string}>({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [orderBookResponse, usersResponse] = await Promise.all([
          api.get(`/competition/${competitionId}/orderbook`),
          api.get(`/competition/${competitionId}/users`)
        ]);

        const usernameMap = usersResponse.data.reduce((acc: any, user: any) => {
          acc[user.id] = user.username;
          return acc;
        }, {});

        setUsernames(usernameMap);
        const tradesWithNames = orderBookResponse.data.trades.map((trade: Trade) => ({
          ...trade,
          buyer_name: usernameMap[trade.buyer_id] || 'Unknown',
          seller_name: usernameMap[trade.seller_id] || 'Unknown'
        }));
        setTrades(tradesWithNames);
      } catch (error) {
        console.error('Failed to fetch trades:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, [competitionId]);

  return (
    <Paper p="md">
      <Text size="xl" weight={700} mb="md">Recent Trades</Text>
      <Table>
        <thead>
          <tr>
            <th>Price</th>
            <th>Quantity</th>
            <th>Parties</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade, i) => (
            <tr key={i}>
              <td>{trade.price.toFixed(2)}</td>
              <td>{trade.quantity}</td>
              <td>{trade.buyer_name} ← {trade.seller_name}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Paper>
  );
}; 