from fastapi import FastAPI, WebSocket, HTTPException, Depends, Header
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
from backend.competition_manager import CompetitionManager
from backend.auth_manager import AuthManager, User
import uuid
import time
from backend.competition_manager.models import Order, OrderSide
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from backend.logger import logger

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

security = HTTPBearer()
auth_manager = AuthManager()
competition_manager = CompetitionManager()

class OrderRequest(BaseModel):
    competition_id: str
    user_id: str
    symbol: str
    side: str
    quantity: int
    price: float

class LoginRequest(BaseModel):
    username: str
    password: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    user = auth_manager.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

async def get_admin_user(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@app.post("/auth/login")
async def login(credentials: LoginRequest):
    token = auth_manager.verify_user(credentials.username, credentials.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Get user data from auth manager
    user = auth_manager._users.get(credentials.username)
    if not user:
        raise HTTPException(status_code=500, detail="User not found after verification")
    
    return {
        "access_token": token,
        "user": {
            "id": credentials.username,
            "username": credentials.username
        }
    }

@app.post("/auth/create-user")
async def create_user(
    request: CreateUserRequest,
    admin: User = Depends(get_admin_user)
):
    success = auth_manager.create_user(
        request.username,
        request.password,
        request.is_admin
    )
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"status": "created"}

@app.post("/competition/create")
async def create_competition(
    name: str,
    duration_minutes: int,
    admin: User = Depends(get_admin_user)
):
    competition_id = competition_manager.create_competition(name, duration_minutes)
    return {"competition_id": competition_id}

@app.post("/competition/join")
async def join_competition(
    competition_id: str,
    user: User = Depends(get_current_user)
):
    success = competition_manager.add_participant(
        competition_id,
        user.username,
        user.username
    )
    if not success:
        raise HTTPException(status_code=400, detail="Competition full or not found")
    return {"status": "joined"}

@app.post("/order")
async def place_order(order: OrderRequest, user: User = Depends(get_current_user)):
    logger.info(f"Trying to place order for user: {order.user_id}")
    if order.user_id != user.username:
        raise HTTPException(status_code=403, detail="Cannot place orders for other users")
        
    competition = competition_manager.active_competitions.get(order.competition_id)
    if not competition or not competition.is_active():
        raise HTTPException(status_code=400, detail="Invalid or inactive competition")
        
    # Convert to internal Order object
    internal_order = Order(
        order_id=f"{user.username}_{str(uuid.uuid4())}",
        user_id=user.username,
        competition_id=order.competition_id,
        symbol=order.symbol,
        side=OrderSide(order.side),
        price=order.price,
        quantity=order.quantity
    )
    
    matches = competition.order_book.add_order(internal_order)
    competition.process_trades(matches)
    
    return {"status": "processed", "trades": len(matches)}

@app.get("/competition/{competition_id}/leaderboard")
async def get_leaderboard(competition_id: str):
    return competition_manager.get_leaderboard(competition_id)

@app.websocket("/ws/{competition_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    competition_id: str,
    user: User = Depends(get_current_user)
):
    await websocket.accept()
    competition = competition_manager.active_competitions.get(competition_id)
    
    if not competition:
        await websocket.close()
        return
        
    try:
        while competition.is_active():
            # Update market prices
            prices = {
                symbol: simulator.generate_next_price()
                for symbol, simulator in competition.market_simulator.items()
            }
            
            # Calculate PnL for all participants
            leaderboard = competition_manager.get_leaderboard(competition_id)
            
            await websocket.send_json({
                "type": "update",
                "prices": prices,
                "leaderboard": leaderboard
            })
            
            await asyncio.sleep(1)
    except:
        pass
    finally:
        await websocket.close()

@app.get("/competition/{competition_id}/orderbook")
async def get_orderbook_state(
    competition_id: str,
    current_user: User = Depends(get_current_user)
):
    competition = competition_manager.active_competitions.get(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
        
    return competition.get_order_book_state()

@app.get("/competition/{competition_id}/users")
async def get_competition_users(
    competition_id: str,
    current_user: User = Depends(get_current_user)
):
    competition = competition_manager.active_competitions.get(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    print("Debug - Participants:", competition.participants)
    
    return [
        {
            "id": user_id,
            "username": participant_data["display_name"],
            "balance": participant_data["balance"]
        }
        for user_id, participant_data in competition.participants.items()
    ]

@app.get("/competition/{competition_id}/participant/{user_id}")
async def get_participant_data(
    competition_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    if current_user.username != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    competition = competition_manager.active_competitions.get(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
        
    participant = competition.participants.get(user_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    positions_with_market_value = {}
    for symbol, quantity in participant.get("positions", {}).items():
        latest_price = competition._get_latest_price(symbol)
        positions_with_market_value[symbol] = {
            "quantity": quantity,
            "average_price": latest_price,
            "market_value": quantity * latest_price
        }
    
    print("Debug - Participants:", )


    return {
        "cash": participant["balance"],
        "positions": positions_with_market_value,
        #"total_pnl": competition.get_participant_pnl(user_id)
    }

@app.get("/competition/{competition_id}/orders/{user_id}")
async def get_user_orders(
    competition_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    if current_user.username != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    competition = competition_manager.active_competitions.get(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
        
    buy_orders = [order for order in competition.order_book.buy_orders if order.user_id == user_id]
    sell_orders = [order for order in competition.order_book.sell_orders if order.user_id == user_id]
    
    return [order.to_dict() for order in buy_orders + sell_orders]

@app.delete("/competition/{competition_id}/order/{order_id}")
async def cancel_order(
    competition_id: str,
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    competition = competition_manager.active_competitions.get(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
        
    success = competition.order_book.cancel_order(order_id, current_user.username)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found or not authorized")
    
    return {"status": "success"}