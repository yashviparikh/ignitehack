import joblib
import os
from .ml import match_partial_split

# Load ML model from the same directory as the app
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ngo_allocation_model.pkl")
try:
    ml_model = joblib.load(model_path)
except FileNotFoundError:
    print(f"Warning: ML model not found at {model_path}. Using rule-based allocation.")
    ml_model = None

# ----------------------------
# Allocation function
# ----------------------------
def get_allocation(donation, ngos):
    """
    Get allocation recommendations for a donation among available NGOs
    
    Args:
        donation: Dict with donation details (id, food_type, quantity, expiry_hours, lat, lon)
        ngos: List of NGO dicts with details (id, name, accepted_food_types, capacity, lat, lon, etc.)
    
    Returns:
        Dict with donation_id, allocations list, and remaining_quantity
    """
    allocations, remaining = match_partial_split(donation, ngos, ml_model)
    return {
        "donation_id": donation["id"],
        "allocations": allocations,
        "remaining_quantity": remaining
    }