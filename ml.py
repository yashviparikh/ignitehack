import random
from math import radians, cos, sin, asin, sqrt
import pandas as pd
import numpy as np
from xgboost import XGBRegressor

# ---------------------------
# Step 1: Generate synthetic NGOs
# ---------------------------
def generate_ngos(num_ngos=25):
    food_types = ["cooked", "bakery", "fruits"]
    ngos = []
    for i in range(1, num_ngos + 1):
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

# ---------------------------
# Step 2: Haversine distance
# ---------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# ---------------------------
# Step 3: Feature engineering
# ---------------------------
def compute_features(donation, ngo, remaining_quantity):
    distance_km = haversine(donation["lat"], donation["lon"], ngo["lat"], ngo["lon"])
    urgency = max(0, 1 - donation["expiry_hours"]/24)
    food_match = 1 if donation["food_type"] in ngo["accepted_food_types"] else 0
    return {
        "distance_km": distance_km,
        "ngo_capacity": ngo["capacity"],
        "remaining_quantity": remaining_quantity,
        "reliability": ngo["reliability"],
        "recent_donations": ngo["recent_donations"],
        "urgency": urgency,
        "food_match": food_match
    }

# ---------------------------
# Step 4: Generate synthetic training data
# ---------------------------
def generate_training_data(num_samples=500):
    data_rows = []
    for _ in range(num_samples):
        ngos = generate_ngos()
        donation = {
            "food_type": random.choice(["cooked", "bakery", "fruits"]),
            "quantity": random.randint(50, 300),
            "expiry_hours": random.randint(1, 12),
            "lat": 12.9716 + random.uniform(-0.02, 0.02),
            "lon": 77.5946 + random.uniform(-0.02, 0.02)
        }
        remaining_quantity = donation["quantity"]
        # Allocate to NGOs using old weighted logic to generate labels
        while remaining_quantity > 0:
            eligible_ngos = [ngo for ngo in ngos if donation["food_type"] in ngo["accepted_food_types"] and ngo["capacity"] > 0]
            if not eligible_ngos:
                break
            # Compute weighted score (old logic)
            scored_ngos = []
            for ngo in eligible_ngos:
                urgency_fit = max(0, 1 - donation["expiry_hours"]/24)
                distance_fit = 1 / (1 + haversine(donation["lat"], donation["lon"], ngo["lat"], ngo["lon"]))
                demand_fit = min(remaining_quantity, ngo["capacity"]) / remaining_quantity
                reliability_fit = ngo["reliability"]
                fairness_fit = 1 / (1 + ngo["recent_donations"])
                score = 0.4*urgency_fit + 0.35*distance_fit + 0.15*demand_fit + 0.07*reliability_fit + 0.03*fairness_fit
                scored_ngos.append((ngo, score))
            scored_ngos.sort(key=lambda x: x[1], reverse=True)
            top_ngo, top_score = scored_ngos[0]
            allocated = min(top_ngo["capacity"], remaining_quantity)
            # Add features + label
            features = compute_features(donation, top_ngo, remaining_quantity)
            features["allocated_quantity"] = allocated  # target
            data_rows.append(features)
            # Update
            remaining_quantity -= allocated
            top_ngo["capacity"] -= allocated
    df = pd.DataFrame(data_rows)
    return df

# ---------------------------
# Step 5: Train ML model
# ---------------------------
print("Generating synthetic training data...")
train_df = generate_training_data()
X_train = train_df.drop(columns=["allocated_quantity"])
y_train = train_df["allocated_quantity"]

print("Training ML model...")
ml_model = XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1)
ml_model.fit(X_train, y_train)
print("ML model trained!")

# ---------------------------
# Step 6: Partial-split allocation using ML
# ---------------------------
def match_partial_split_ml(donation, ngos, ml_model):
    remaining_quantity = donation["quantity"]
    allocations = []

    while remaining_quantity > 0:
        eligible_ngos = [ngo for ngo in ngos if donation["food_type"] in ngo["accepted_food_types"] and ngo["capacity"] > 0]
        if not eligible_ngos:
            break

        # Compute features
        feature_list = [compute_features(donation, ngo, remaining_quantity) for ngo in eligible_ngos]
        df_features = pd.DataFrame(feature_list)

        # ML model predicts allocation score
        scores = ml_model.predict(df_features)
        scored_ngos = sorted(zip(eligible_ngos, scores), key=lambda x: x[1], reverse=True)

        # Allocate to top NGO
        top_ngo, top_score = scored_ngos[0]
        allocated = min(top_ngo["capacity"], remaining_quantity)
        allocations.append({"ngo_name": top_ngo["name"], "allocated_quantity": allocated, "score": top_score})

        remaining_quantity -= allocated
        top_ngo["capacity"] -= allocated

    return allocations, remaining_quantity

# ---------------------------
# Step 7: Example usage
# ---------------------------
random.seed(42)
ngos = generate_ngos()

print("=== NGOs ===")
for ngo in ngos:
    print(f"{ngo['name']} | Capacity: {ngo['capacity']} | Food types: {ngo['accepted_food_types']}")

donation = {
    "id": 1,
    "food_type": "cooked",
    "quantity": 900,
    "expiry_hours": 14,
    "lat": 12.9716,
    "lon": 77.5946
}

# allocations, remaining = match_partial_split_ml(donation, ngos, ml_model)

# print("\n=== Donation Allocation (ML-driven) ===")
# for alloc in allocations:
#     print(f"{alloc['ngo_name']} receives {alloc['allocated_quantity']} meals (Score: {alloc['score']:.3f})")

# if remaining > 0:
#     print(f"\nRemaining {remaining} meals offered to public volunteers")
# else:
#     print("\nAll donation allocated to NGOs")


def generate_donations(n=10):
    food_types = ["cooked", "bakery", "fruits"]
    donations = []
    for i in range(1, n+1):
        donation = {
            "id": i,
            "food_type": random.choice(food_types),
            "quantity": random.randint(50, 300),
            "expiry_hours": random.randint(1, 12),
            "lat": 12.9716 + random.uniform(-0.01, 0.01),
            "lon": 77.5946 + random.uniform(-0.01, 0.01)
        }
        donations.append(donation)
    return donations
def allocate_multiple_donations(donations, ngos):
    all_allocations = []
    total_allocated = 0
    total_donations = sum(d["quantity"] for d in donations)
    
    for donation in donations:
        allocations, remaining = match_partial_split_ml(donation, ngos,ml_model)
        all_allocations.append({
            "donation_id": donation["id"],
            "allocations": allocations,
            "remaining": remaining
        })
        total_allocated += sum(a["allocated_quantity"] for a in allocations)
    
    accuracy = total_allocated / total_donations
    return all_allocations, accuracy
donations = generate_donations(n=10)  # generate 10 test donations

allocations, accuracy = allocate_multiple_donations(donations, ngos)

for alloc in allocations:
    print(f"\nDonation {alloc['donation_id']} allocation:")
    for a in alloc['allocations']:
        print(f"  {a['ngo_name']} receives {a['allocated_quantity']} meals (Score: {a['score']})")
    if alloc['remaining'] > 0:
        print(f"  Remaining {alloc['remaining']} meals offered to public volunteers")

print(f"\nOverall allocation accuracy: {accuracy*100:.2f}%")
