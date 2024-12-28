export interface Order {
    price: number;
    quantity: number;
    user_id: string;
}

export interface Trade {
    price: number;
    quantity: number;
    buyer_id: string;
    seller_id: string;
}

export interface OrderBookState {
    buy_orders: Order[];
    sell_orders: Order[];
    trades: Trade[];
} 