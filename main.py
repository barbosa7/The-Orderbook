import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.API import app, auth_manager

def setup_initial_data():
    try:
        auth_manager.create_user("admin", "admin_password", is_admin=True)
        print("Created admin user successfully")
        
        auth_manager.create_user("trader1", "pass123", is_admin=False)
        auth_manager.create_user("trader2", "pass456", is_admin=False)
        auth_manager.create_user("trader3", "pass456", is_admin=False)
        auth_manager.create_user("trader4", "pass456", is_admin=False)
        print("Created test users successfully")
    except Exception as e:
        print(f"Error creating initial users: {e}")

setup_initial_data()
