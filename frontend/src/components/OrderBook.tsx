import { useEffect, useState } from 'react';
import { Table, Text, Paper, Group, Stack } from '@mantine/core';
import { api } from '../services/api';
import { OrderBookState } from '../types';

interface Props {
  competitionId: string;
}

interface PriceLevel {
  price: number;
  quantity: number;
  user_id: string;
}

interface FormattedOrderBook {
  prices: number[];
  bids: { [price: number]: PriceLevel };
  asks: { [price: number]: PriceLevel };
}

export const OrderBook: React.FC<Props> = ({ competitionId }) => {
  const [orderBook, setOrderBook] = useState<OrderBookState | null>(null);
  const [formattedBook, setFormattedBook] = useState<FormattedOrderBook>({
    prices: [],
    bids: {},
    asks: {}
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const { data } = await api.get(`/competition/${competitionId}/orderbook`);
        setOrderBook(data);

        // Format order book data
        const prices = new Set<number>();
        const bids: { [price: number]: PriceLevel } = {};
        const asks: { [price: number]: PriceLevel } = {};

        data.buy_orders.forEach((order: PriceLevel) => {
          prices.add(order.price);
          bids[order.price] = order;
        });

        data.sell_orders.forEach((order: PriceLevel) => {
          prices.add(order.price);
          asks[order.price] = order;
        });

        setFormattedBook({
          prices: Array.from(prices).sort((a, b) => b - a), // Sort descending
          bids,
          asks
        });
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, [competitionId]);

  if (!orderBook) return null;

  return (
    <Paper p="md">
      <Text size="xl" weight={700} mb="md" align="center">Order Book</Text>
      <Table striped>
        <thead>
          <tr>
            <th style={{ textAlign: 'right' }}>Bid Size</th>
            <th style={{ textAlign: 'center' }}>Price</th>
            <th style={{ textAlign: 'left' }}>Ask Size</th>
          </tr>
        </thead>
        <tbody>
          {formattedBook.prices.map((price, index) => (
            <tr key={index}>
              <td style={{ textAlign: 'right' }}>{formattedBook.bids[price]?.quantity || 0}</td>
              <td style={{ textAlign: 'center' }}>{price.toFixed(2)}</td>
              <td style={{ textAlign: 'left' }}>{formattedBook.asks[price]?.quantity || 0}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Paper>
  );
}; 