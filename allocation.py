import joblib
from ml import match_partial_split
ml_model = joblib.load("ngo_allocation_model.pkl")
# ----------------------------
# Allocation function
# ----------------------------
def get_allocation(donation,ngos):
    ngos =ngos
    allocations, remaining = match_partial_split(donation, ngos, ml_model)
    return {
        "donation_id": donation["id"],
        "allocations": allocations,
        "remaining_quantity": remaining
    }
# ngos = [
#     {
#         "id": 1,
#         "name": "NGO_1",
#         "accepted_food_types": ["Dairy Products", "Frozen Foods"],
#         "capacity": 96,
#         "lat": 12.977980260385616,
#         "lon": 77.5934550337575,
#         "reliability": 0.84,
#         "recent_donations": 3,
#         "schedule": "dinner"
#     },
#     {
#         "id": 2,
#         "name": "NGO_2",
#         "accepted_food_types": ["Bakery Items", "Other", "Meat & Seafood"],
#         "capacity": 194,
#         "lat": 12.989101732483828,
#         "lon": 77.59770279299,
#         "reliability": 0.87,
#         "recent_donations": 4,
#         "schedule": "lunch"
#     },
#     {
#         "id": 3,
#         "name": "NGO_3",
#         "accepted_food_types": ["Beverages", "Bakery Items"],
#         "capacity": 55,
#         "lat": 12.98826261834225,
#         "lon": 77.61572224159502,
#         "reliability": 0.86,
#         "recent_donations": 2,
#         "schedule": "dinner"
#     },
#     {
#         "id": 4,
#         "name": "NGO_4",
#         "accepted_food_types": ["Canned Goods", "Meat & Seafood"],
#         "capacity": 89,
#         "lat": 12.981423696463512,
#         "lon": 77.60317061319925,
#         "reliability": 0.82,
#         "recent_donations": 5,
#         "schedule": "lunch"
#     },
#     {
#         "id": 5,
#         "name": "NGO_5",
#         "accepted_food_types": ["Prepared Meals"],
#         "capacity": 71,
#         "lat": 12.98445456284463,
#         "lon": 77.60879464170826,
#         "reliability": 0.79,
#         "recent_donations": 4,
#         "schedule": "dinner"
#     },
#     {
#         "id": 6,
#         "name": "NGO_6",
#         "accepted_food_types": ["Frozen Foods", "Canned Goods"],
#         "capacity": 103,
#         "lat": 12.960024378155497,
#         "lon": 77.61800291164006,
#         "reliability": 0.88,
#         "recent_donations": 3,
#         "schedule": "dinner"
#     }
# ]

# donation = {
#         "id": 1,
#         "food_type": "Bakery Items",
#         "quantity": 17,
#         "expiry_hours": 3,
#         "lat": 12.9716,
#         "lon": 77.5946
#     }
# print(get_allocation(donation=donation,ngos=ngos))