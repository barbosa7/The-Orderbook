# Example setup
competition_manager = CompetitionManager()

# Create a new competition
competition_id = competition_manager.create_competition("Algo Trading Cup", 60)

# Add instruments
competition = competition_manager.active_competitions[competition_id]
competition.add_instrument(Instrument(
    symbol="AAPL",
    initial_price=150.0,
    tick_size=0.01,
    lot_size=100,
    volatility=0.002
))

# Add participants
competition_manager.add_participant(competition_id, "user1", "Alice")
competition_manager.add_participant(competition_id, "user2", "Bob")

# Initialize the system
auth_manager = AuthManager()

# Admin creates the first admin user
auth_manager.create_user("admin", "admin_password", is_admin=True)

# Admin creates regular users
auth_manager.create_user("trader1", "pass123")
auth_manager.create_user("trader2", "pass456")

# Users can then login and receive JWT tokens for subsequent requests
