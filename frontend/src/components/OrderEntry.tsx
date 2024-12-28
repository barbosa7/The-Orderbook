import { useState } from 'react';
import { Paper, TextInput, NumberInput, Select, Button, Group } from '@mantine/core';
import { placeOrder } from '../services/api';
import { showNotification } from '@mantine/notifications';

interface Props {
  competitionId: string;
  symbol: string;
}

export const OrderEntry: React.FC<Props> = ({ competitionId, symbol }) => {
  const [orderData, setOrderData] = useState({
    side: 'BUY',
    quantity: 0,
    price: 0,
  });

  const handleSubmit = async () => {
    try {
      await placeOrder({
        competition_id: competitionId,
        symbol,
        ...orderData,
        quantity: Math.floor(orderData.quantity),
      });
      showNotification({
        title: 'Success',
        message: 'Order placed successfully',
        color: 'green',
      });
    } catch (error) {
      showNotification({
        title: 'Error',
        message: 'Failed to place order',
        color: 'red',
      });
    }
  };

  return (
    <Paper p="md">
      <Select
        label="Side"
        value={orderData.side}
        onChange={(value) => setOrderData({ ...orderData, side: value as 'BUY' | 'SELL' })}
        data={[
          { value: 'BUY', label: 'Buy' },
          { value: 'SELL', label: 'Sell' },
        ]}
      />
      <NumberInput
        label="Quantity"
        value={orderData.quantity}
        onChange={(value) => setOrderData({ ...orderData, quantity: value || 0 })}
        min={1}
        step={1}
      />
      <NumberInput
        label="Price"
        value={orderData.price}
        onChange={(value) => setOrderData({ ...orderData, price: value || 0 })}
        min={0.01}
        step={0.01}
        precision={2}
      />
      <Button 
        fullWidth 
        mt="md"
        onClick={handleSubmit}
        color={orderData.side === 'BUY' ? 'green' : 'red'}
      >
        Place {orderData.side} Order
      </Button>
    </Paper>
  );
}; 