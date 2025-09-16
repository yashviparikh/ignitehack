import random
from math import radians, cos, sin, asin, sqrt

# Function to generate synthetic NGOs
def testing():
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

# Scoring function
def compute_ngo_score(donation, ngo):
    w_urgency = 0.35
    w_distance = 0.30
    w_demand = 0.20
    w_reliability = 0.10
    w_fairness = 0.05
    
    urgency_fit = max(0, 1 - donation["expiry_hours"]/24)
    distance_km = haversine(donation["lat"], donation["lon"], ngo["lat"], ngo["lon"])
    distance_fit = 1 / (1 + distance_km)
    demand_fit = min(donation["quantity"], ngo["capacity"]) / donation["quantity"]
    reliability_fit = ngo["reliability"]
    fairness_fit = 1 / (1 + ngo["recent_donations"])
    
    score = (
        w_urgency * urgency_fit +
        w_distance * distance_fit +
        w_demand * demand_fit +
        w_reliability * reliability_fit +
        w_fairness * fairness_fit
    )
    return score

# Match donation to NGO
def match_donation_to_ngo(donation, ngos):
    eligible_ngos = [
        ngo for ngo in ngos
        if donation["food_type"] in ngo["accepted_food_types"]
        and ngo["capacity"] >= donation["quantity"]
    ]
    
    if not eligible_ngos:
        return None
    
    scores = [(ngo, compute_ngo_score(donation, ngo)) for ngo in eligible_ngos]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[0][0]

# Generate NGOs
ngos = testing()

# Print full NGO list
print("=== List of NGOs ===")
for ngo in ngos:
    print(f"ID: {ngo['id']}, Name: {ngo['name']}, Food Types: {ngo['accepted_food_types']}, Capacity: {ngo['capacity']}, Reliability: {ngo['reliability']}, Recent Donations: {ngo['recent_donations']}, Schedule: {ngo['schedule']}")

# Sample donation
donation = {
    "id": 1,
    "food_type": "cooked",
    "quantity": 100,
    "expiry_hours": 4,
    "lat": 12.9716,
    "lon": 77.5946
}

# Match donation
top_ngo = match_donation_to_ngo(donation, ngos)
print("\n=== Matching Result ===")
print("Top NGO Match:", top_ngo["name"] if top_ngo else "No NGO available")
