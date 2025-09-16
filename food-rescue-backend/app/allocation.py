import joblib
import os
from .ml import match_partial_split

# Load ML model from the same directory as the app (ML-FIRST APPROACH)
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ngo_allocation_model.pkl")
try:
    ml_model = joblib.load(model_path)
    print(f"✅ ML model loaded successfully from: {model_path}")
    print("🧠 ML-First allocation mode enabled!")
except FileNotFoundError:
    print(f"⚠️ ML model not found at: {model_path}")
    print("🔄 Rule-based fallback mode will be used for all allocations")
    ml_model = None
except Exception as e:
    print(f"❌ Error loading ML model: {e}")
    print("🔄 Rule-based fallback mode will be used for all allocations")
    ml_model = None

# ----------------------------
# Allocation function
# ----------------------------
def get_allocation(donation, ngos):
    """
    Get allocation recommendations for a donation among available NGOs
    Uses ML-FIRST approach: ML model primary, rule-based fallback
    
    Args:
        donation: Dict with donation details (id, food_type, quantity, expiry_hours, lat, lon)
        ngos: List of NGO dicts with details (id, name, accepted_food_types, capacity, lat, lon, etc.)
    
    Returns:
        Dict with donation_id, allocations list, remaining_quantity, and allocation_method
    """
    print(f"🍽️ Processing allocation for donation {donation['id']}: {donation['food_type']} ({donation['quantity']} units)")
    print(f"📍 Available NGOs: {len(ngos)}")
    print("🔧 DEBUG: Using UPDATED allocation.py function with additional fields")
    
    allocations, remaining = match_partial_split(donation, ngos, ml_model)
    
    # Determine which method was used based on allocation results
    method_used = "Mixed"
    if allocations:
        if all(alloc.get("allocation_method") == "ML" for alloc in allocations):
            method_used = "ML"
        elif all(alloc.get("allocation_method") == "Rule-Based" for alloc in allocations):
            method_used = "Rule-Based"
    
    result = {
        "donation_id": donation["id"],
        "allocations": allocations,
        "remaining_quantity": remaining,
        "allocation_method": method_used,
        "total_allocated": donation["quantity"] - remaining,
        "ngos_matched": len(allocations)
    }
    
    print(f"✅ Allocation complete: {len(allocations)} NGOs matched using {method_used} method")
    return result