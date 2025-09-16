import random
import math
from math import radians, cos, sin, asin, sqrt
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor

# ----------------------------
# Generate synthetic NGOs
# ----------------------------
def generate_ngos(num_ngos=25):
    food_types = [
        "Fresh Produce",
        "Dairy Products",
        "Bakery Items",
        "Meat & Seafood",
        "Prepared Meals",
        "Canned Goods",
        "Frozen Foods",
        "Beverages",
        "Other"
    ]
    ngos = []
    for i in range(1, num_ngos + 1):
        ngo = {
            "id": i,
            "name": f"NGO_{i}",
            "accepted_food_types": random.sample(food_types, k=random.randint(1, 3)),
            "capacity": random.randint(50, 200),
            "lat": 12.9600 + random.uniform(0, 0.03),
            "lon": 77.5900 + random.uniform(0, 0.03),
            "reliability": round(random.uniform(0.75, 0.95), 2),
            "recent_donations": random.randint(0, 5),
            "schedule": random.choice(["lunch", "dinner"])
        }
        ngos.append(ngo)
    return ngos

# ----------------------------
# Haversine distance
# ----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    return R * c

# ----------------------------
# Compute NGO score (weighted)
# ----------------------------
def compute_ngo_score(donation, ngo, remaining_quantity):
    if remaining_quantity <= 0:
        return 0

    w_urgency = 0.25
    w_distance = 0.40
    w_capacity = 0.20
    w_reliability = 0.10
    w_fairness = 0.05

    urgency_fit = max(0, 1 - donation["expiry_hours"]/24)
    distance_km = haversine(donation["lat"], donation["lon"], ngo["lat"], ngo["lon"])
    distance_fit = math.exp(-0.15 * distance_km)
    capacity_fit = min(ngo["capacity"], remaining_quantity) / remaining_quantity
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

    eligible_ngos = [
        ngo for ngo in ngos
        if donation["food_type"] in ngo["accepted_food_types"] and ngo["capacity"] > 0
    ]
    if not eligible_ngos:
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
            "score": round(top_score, 3)
        })

        remaining_quantity -= allocated
        top_ngo["capacity"] -= allocated
        eligible_ngos = [ngo for ngo in eligible_ngos if ngo["capacity"] > 0]

    return allocations, remaining_quantity

# ----------------------------
# Synthetic training data
# ----------------------------
def generate_training_data(ngos, n_samples=500):
    X, y = [], []
    for _ in range(n_samples):
        donation_qty = random.randint(50, 300)
        donation_food = random.choice(["Fresh Produce", "Bakery Items", "Dairy Products"])
        donation = {
            "quantity": donation_qty,
            "food_type": donation_food,
            "expiry_hours": random.randint(1, 6),
            "lat": 12.9716,
            "lon": 77.5946
        }
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
# Main: Train ML model
# ----------------------------
if __name__ == "__main__":
    random.seed(42)
    ngos = generate_ngos()

    print("Generating synthetic training data...")
    X_train, y_train = generate_training_data(ngos, n_samples=1000)

    print("Training ML model...")
    ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
    ml_model.fit(X_train, y_train)

    joblib.dump(ml_model, "ngo_allocation_model.pkl")
    print("✅ Model trained and saved as ngo_allocation_model.pkl")
