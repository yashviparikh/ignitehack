import numpy as np
from typing import List, Dict, Tuple
from geopy.distance import geodesic

def match_partial_split(donation: Dict, ngos: List[Dict], ml_model) -> Tuple[List[Dict], int]:
    """
    Allocate donation to NGOs using ML model and business logic
    
    Args:
        donation: Dict with keys: id, food_type, quantity, expiry_hours, lat, lon
        ngos: List of NGO dicts with keys: id, name, accepted_food_types, capacity, lat, lon, reliability, recent_donations, schedule
        ml_model: Trained ML model for allocation predictions
    
    Returns:
        Tuple of (allocations, remaining_quantity)
        allocations: List of dicts with ngo_id, allocated_quantity, priority_score
        remaining_quantity: Amount not allocated
    """
    
    allocations = []
    remaining_quantity = donation["quantity"]
    
    if remaining_quantity <= 0:
        return allocations, remaining_quantity
    
    # Filter NGOs that accept this food type
    compatible_ngos = []
    for ngo in ngos:
        accepted_types = ngo.get("accepted_food_types", [])
        if isinstance(accepted_types, str):
            import json
            try:
                accepted_types = json.loads(accepted_types)
            except:
                accepted_types = [accepted_types]
        
        if donation["food_type"] in accepted_types:
            compatible_ngos.append(ngo)
    
    if not compatible_ngos:
        return allocations, remaining_quantity
    
    # Calculate features for each compatible NGO
    ngo_features = []
    for ngo in compatible_ngos:
        try:
            # Calculate distance
            donation_coords = (donation["lat"], donation["lon"])
            ngo_coords = (ngo["lat"], ngo["lon"])
            distance_km = geodesic(donation_coords, ngo_coords).kilometers
            
            # Create feature vector for ML model
            features = [
                distance_km,
                ngo.get("capacity", 100),
                ngo.get("reliability", 0.8),
                ngo.get("recent_donations", 0),
                donation.get("expiry_hours", 24),
                donation.get("quantity", 0)
            ]
            
            ngo_features.append({
                "ngo": ngo,
                "features": features,
                "distance": distance_km
            })
        except Exception as e:
            print(f"Error calculating features for NGO {ngo.get('id', 'unknown')}: {e}")
            continue
    
    if not ngo_features:
        return allocations, remaining_quantity
    
    # Sort by priority: distance, capacity, reliability
    ngo_features.sort(key=lambda x: (
        x["distance"],  # Closer is better
        -x["ngo"].get("capacity", 100),  # Higher capacity is better
        -x["ngo"].get("reliability", 0.8)  # Higher reliability is better
    ))
    
    # Use ML model to predict allocation scores if available (ML-FIRST APPROACH)
    ml_predictions_successful = False
    
    if ml_model is not None:
        try:
            print("🧠 Using ML model for allocation predictions...")
            for ngo_data in ngo_features:
                features_array = np.array([ngo_data["features"]])
                prediction = ml_model.predict(features_array)[0]
                ngo_data["ml_score"] = prediction
            ml_predictions_successful = True
            print(f"✅ ML predictions successful for {len(ngo_features)} NGOs")
        except Exception as e:
            print(f"❌ ML model prediction failed: {e}")
            print("🔄 Falling back to rule-based scoring...")
            # Fall back to rule-based scoring
            for ngo_data in ngo_features:
                ngo_data["ml_score"] = _calculate_rule_based_score(ngo_data)
    else:
        print("⚠️ No ML model available, using rule-based scoring...")
        # No ML model, use rule-based scoring
        for ngo_data in ngo_features:
            ngo_data["ml_score"] = _calculate_rule_based_score(ngo_data)
    
    # Sort by ML score (descending) - ML predictions take priority
    ngo_features.sort(key=lambda x: -x["ml_score"])
    
    # Allocate donations based on scores and capacity
    for ngo_data in ngo_features:
        if remaining_quantity <= 0:
            break
            
        ngo = ngo_data["ngo"]
        ngo_capacity = ngo.get("capacity", 100)
        
        # Allocate up to NGO capacity or remaining quantity
        allocated_amount = min(remaining_quantity, ngo_capacity)
        
        if allocated_amount > 0:
            allocation_entry = {
                "ngo_id": ngo["id"],
                "ngo_name": ngo["name"],
                "allocated_quantity": allocated_amount,
                "priority_score": round(ngo_data["ml_score"], 3),
                "distance_km": round(ngo_data["distance"], 2),
                "reliability": ngo.get("reliability", 0.8),
                "capacity": ngo_capacity,
                "allocation_method": "ML" if ml_predictions_successful else "Rule-Based"
            }
            allocations.append(allocation_entry)
            remaining_quantity -= allocated_amount
    
    # Log allocation summary
    if allocations:
        method = "ML" if ml_predictions_successful else "Rule-Based"
        print(f"📊 Allocation complete using {method} method: {len(allocations)} NGOs allocated")
    
    return allocations, remaining_quantity


def _calculate_rule_based_score(ngo_data: Dict) -> float:
    """
    Calculate allocation score using rule-based approach (FALLBACK METHOD)
    This is used when ML model is unavailable or fails
    """
    ngo = ngo_data["ngo"]
    distance = ngo_data["distance"]
    
    # Base score components
    distance_score = max(0, 100 - distance * 2)  # Penalty for distance
    capacity_score = min(100, ngo.get("capacity", 100))  # Capacity bonus
    reliability_score = ngo.get("reliability", 0.8) * 100  # Reliability bonus
    
    # Recent donations penalty (spread the load)
    recent_penalty = ngo.get("recent_donations", 0) * 5
    
    # Combine scores with weighted approach
    total_score = (
        distance_score * 0.4 +  # 40% weight on distance (closer is better)
        capacity_score * 0.3 +  # 30% weight on capacity (higher is better)
        reliability_score * 0.3  # 30% weight on reliability (higher is better)
        - recent_penalty  # Penalty for recent donations (spread load)
    )
    
    return max(0, total_score)