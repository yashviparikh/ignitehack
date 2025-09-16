import random 
import math
from math import radians, cos, sin, asin, sqrt
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# ----------------------------
# Generate synthetic NGOs
# ----------------------------
def generate_ngos():
    food_types = ["Fresh Produce",
    "Dairy Products",
    "Bakery Items",
    "Meat & Seafood",
    "Prepared Meals",
    "Canned Goods",
    "Frozen Foods",
    "Beverages",
    "Other"]
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

# ----------------------------
# Haversine distance
# ----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    return R * c

# ----------------------------
# Compute weighted NGO score (no priority fill, all weights only)
# ----------------------------
def compute_ngo_score(donation, ngo, remaining_quantity):
    if remaining_quantity <= 0:
        return 0
    # Adjusted realistic weights
    w_urgency = 0.25
    w_distance = 0.40
    w_capacity = 0.20
    w_reliability = 0.10
    w_fairness = 0.05

    # Urgency fit (higher if less time left before expiry)
    urgency_fit = max(0, 1 - donation["expiry_hours"]/24)

    # Distance fit (exponential decay, closer NGOs get higher score)
    distance_km = haversine(donation["lat"], donation["lon"], ngo["lat"], ngo["lon"])
    distance_fit = math.exp(-0.15 * distance_km)

    # Capacity fit (how much of the donation this NGO can realistically take)
    capacity_fit = min(ngo["capacity"], remaining_quantity) / remaining_quantity

    # Reliability & fairness
    reliability_fit = ngo["reliability"]
    fairness_fit = 1 / (1 + ngo["recent_donations"])

    score = (
        w_urgency * urgency_fit +
        w_distance * distance_fit +
        w_capacity * capacity_fit +
        w_reliability * reliability_fit +
        w_fairness * fairness_fit
    )
    return score

# ----------------------------
# Partial-split allocation
# ----------------------------
def match_partial_split(donation, ngos, ml_model=None):
    remaining_quantity = donation["quantity"]
    allocations = []

    # Filter eligible NGOs
    eligible_ngos = [ngo for ngo in ngos if donation["food_type"] in ngo["accepted_food_types"] and ngo["capacity"] > 0]
    if not eligible_ngos:
        print("No eligible NGOs, donation goes to public volunteers.")
        return allocations, remaining_quantity

    while remaining_quantity > 0 and eligible_ngos:
        scored_ngos = []
        for ngo in eligible_ngos:
            score = compute_ngo_score(donation, ngo, remaining_quantity)
            if ml_model:
                features = [
                    remaining_quantity,
                    ngo["capacity"],
                    haversine(donation["lat"], donation["lon"], ngo["lat"], ngo["lon"]),
                    ngo["reliability"],
                    ngo["recent_donations"]
                ]
                score = ml_model.predict([features])[0]
            scored_ngos.append((ngo, score))
        
        scored_ngos.sort(key=lambda x: x[1], reverse=True)
        top_ngo, top_score = scored_ngos[0]

        allocated = min(top_ngo["capacity"], remaining_quantity)
        allocations.append({
            "ngo_name": top_ngo["name"],
            "allocated_quantity": allocated,
            "score": round(top_score,3)
        })

        print(f"Allocating {allocated} meals to {top_ngo['name']} (Score: {top_score:.3f}, NGO Capacity: {top_ngo['capacity']})")

        # Update
        remaining_quantity -= allocated
        top_ngo["capacity"] -= allocated
        eligible_ngos = [ngo for ngo in eligible_ngos if ngo["capacity"] > 0]

    return allocations, remaining_quantity

# ----------------------------
# Synthetic training data for ML
# ----------------------------
def generate_training_data(ngos, n_samples=500):
    X, y = [], []
    for _ in range(n_samples):
        donation_qty = random.randint(50, 300)
        donation_food = random.choice(["cooked","bakery","fruits"])
        donation = {"quantity": donation_qty, "food_type": donation_food, "expiry_hours": random.randint(1,6), "lat": 12.9716, "lon": 77.5946}
        for ngo in ngos:
            if donation_food in ngo["accepted_food_types"]:
                features = [
                    donation_qty,
                    ngo["capacity"],
                    haversine(donation["lat"], donation["lon"], ngo["lat"], ngo["lon"]),
                    ngo["reliability"],
                    ngo["recent_donations"]
                ]
                score = compute_ngo_score(donation, ngo, donation_qty)
                X.append(features)
                y.append(score)
    return np.array(X), np.array(y)

# ----------------------------
# Main
# ----------------------------
random.seed(42)
ngos = generate_ngos()

# Train ML model
print("Generating synthetic training data...")
X_train, y_train = generate_training_data(ngos, n_samples=1000)
ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
print("Training ML model...")
ml_model.fit(X_train, y_train)
print("ML model trained!\n")

# Print NGOs
print("=== NGOs ===")
for ngo in ngos:
    print(f"{ngo['name']} | Capacity: {ngo['capacity']} | Food types: {ngo['accepted_food_types']}")

# Generate multiple donations
donations = []
for i in range(10):
    donations.append({
        "id": i+1,
        "food_type": random.choice(["cooked","bakery","fruits"]),
        "quantity": random.randint(50,300),
        "expiry_hours": random.randint(1,6),
        "lat": 12.9716,
        "lon": 77.5946
    })

# Allocate donations & compute allocation accuracy
correct_allocations = 0
total_meals = 0
for donation in donations:
    print(f"\n=== Donation {donation['id']} allocation ===")
    allocations, remaining = match_partial_split(donation, ngos, ml_model)
    allocated_sum = sum(a['allocated_quantity'] for a in allocations)
    total_meals += donation["quantity"]
    correct_allocations += allocated_sum
    for alloc in allocations:
        print(f"  {alloc['ngo_name']} receives {alloc['allocated_quantity']} meals (Score: {alloc['score']})")
    if remaining > 0:
        print(f"  Remaining {remaining} meals offered to public volunteers")

accuracy = correct_allocations / total_meals * 100
print(f"\nOverall allocation accuracy: {accuracy:.2f}%")
