import random
from math import radians, cos, sin, asin, sqrt

# Generate synthetic NGOs
def generate_ngos():
    food_types = ["cooked", "bakery", "fruits"]
    ngos = []
    for i in range(1, 26):
        ngo = {
            "id": i,
            "name": f"NGO_{i}",
            "accepted_food_types": random.sample(food_types, k=random.randint(1,3)),
            "capacity": random.randint(50, 200),
            "lat": 12.9600 + random.uniform(0, 0.03),
            "lon": 77.5900 + random.uniform(0, 0.03),
            "reliability": round(random.uniform(0.75, 0.95), 2),
            "recent_donations": random.randint(0,5),
            "schedule": random.choice(["lunch", "dinner"])
        }
        ngos.append(ngo)
    return ngos

# Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# Compute weighted NGO score (dynamic demand_fit)
def compute_ngo_score(donation, ngo, remaining_quantity):
    if remaining_quantity <= 0:
        return 0 
    # Weights (urgency & distance emphasized)
    w_urgency = 0.4
    w_distance = 0.35
    w_demand = 0.15
    w_reliability = 0.07
    w_fairness = 0.03

    # Urgency fit
    urgency_fit = max(0, 1 - donation["expiry_hours"]/24)
    
    # Distance fit
    distance_km = haversine(donation["lat"], donation["lon"], ngo["lat"], ngo["lon"])
    distance_fit = 1 / (1 + distance_km)
    
    # Dynamic demand fit
    demand_fit = min(remaining_quantity, ngo["capacity"]) / remaining_quantity
    
    # Reliability & Fairness
    reliability_fit = ngo["reliability"]
    fairness_fit = 1 / (1 + ngo["recent_donations"])
    
    # Weighted score
    score = (
        w_urgency * urgency_fit +
        w_distance * distance_fit +
        w_demand * demand_fit +
        w_reliability * reliability_fit +
        w_fairness * fairness_fit
    )
    return score

# Partial-split allocation
def match_partial_split(donation, ngos):
    remaining_quantity = donation["quantity"]
    allocations = []
    # Filter eligible NGOs
    eligible_ngos = [ngo for ngo in ngos if donation["food_type"] in ngo["accepted_food_types"] and ngo["capacity"] > 0]
    
    if not eligible_ngos:
        print("No eligible NGOs, entire donation goes to public volunteers.")
        return allocations, remaining_quantity

    # Print scores for all eligible NGOs before allocation
    print("\n=== NGO Scores Before Allocation ===")
    scored_ngos = [(ngo, compute_ngo_score(donation, ngo, remaining_quantity)) for ngo in eligible_ngos]
    scored_ngos.sort(key=lambda x: x[1], reverse=True)
    for ngo, score in scored_ngos:
        print(f"{ngo['name']} | Capacity: {ngo['capacity']} | Score: {score:.3f}")

    # Allocate donation
    while remaining_quantity > 0 and scored_ngos:
        top_ngo, top_score = scored_ngos[0]
        allocated = min(top_ngo["capacity"], remaining_quantity)
        allocations.append({"ngo_name": top_ngo["name"], "allocated_quantity": allocated, "score": round(top_score,3)})

        print(f"\nAllocating {allocated} meals to {top_ngo['name']} (Score: {top_score:.3f}, NGO Capacity: {top_ngo['capacity']})")

        # Update remaining quantity & NGO capacity
        remaining_quantity -= allocated
        top_ngo["capacity"] -= allocated

        # Recompute scores for remaining NGOs
        scored_ngos = [(ngo, compute_ngo_score(donation, ngo, remaining_quantity)) for ngo in eligible_ngos if ngo["capacity"] > 0]
        scored_ngos.sort(key=lambda x: x[1], reverse=True)

    return allocations, remaining_quantity

# Example usage
random.seed(42)
ngos = generate_ngos()

# Print NGO list
print("=== NGOs ===")
for ngo in ngos:
    print(f"{ngo['name']} | Capacity: {ngo['capacity']} | Food types: {ngo['accepted_food_types']}")

# Sample donation
donation = {
    "id": 1,
    "food_type": "cooked",
    "quantity": 300,
    "expiry_hours": 4,
    "lat": 12.9716,
    "lon": 77.5946
}

# Match donation
allocations, remaining = match_partial_split(donation, ngos)

print("\n=== Donation Allocation ===")
for alloc in allocations:
    print(f"{alloc['ngo_name']} receives {alloc['allocated_quantity']} meals (Score: {alloc['score']})")

if remaining > 0:
    print(f"\nRemaining {remaining} meals offered to public volunteers")
else:
    print("\nAll donation allocated to NGOs")
