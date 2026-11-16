# Carbon & water emission factors and configuration constants

CAT_FACTORS = {
    "Wood / plywood": (0.9, 50),
    "Fabric / costume": (15.0, 6000),
    "Plastic": (3.0, 200),
    "Metal": (4.0, 300),
    "Paper / cardboard": (1.3, 400),
    "Glass / ceramic": (1.2, 30),
    "Furniture / finished goods": (2.5, 300),
    "Electronics": (20.0, 1500),
    "Paint / chemicals": (3.0, 100),
    "Other": (2.0, 200),
}

# method: (Display Name, is_online, production_multiplier, packaging_kgCO2e_per_parcel)
METHOD_FACTORS = {
    "coupang": ("Coupang", True, 1.0, 0.55),
    "naver": ("Naver Shopping", True, 1.0, 0.70),
    "daiso": ("Daiso store", False, 1.0, 0.0),
    "danggeun": ("Danggeun (used)", False, 0.05, 0.0),
    "rental": ("Prop rental house", False, 0.03, 0.0),
    "reuse": ("Reuse from stock / scrap", False, 0.01, 0.0),
}

# mode: (Display Name, kgCO2e_per_km)
MODE_FACTORS = {
    "walk": ("Walk / bike", 0.0),
    "transit": ("Public transit", 0.07),
    "car": ("Car", 0.19),
    "van": ("Van / truck", 0.28),
}

TRUCK_FACTOR = 0.00015      # freight kgCO2e per kg-km
ROAD_MULTIPLIER = 1.3       # straight-line to road distance fallback multiplier
MEAL_CO2E = 2.0             # kgCO2e per meal
DRINK_WATER_L = 2.0         # L per person per day
TREE_CO2E_YEAR = 6.6        # kgCO2e absorbed per tree per year
THRESHOLD_MID = 20.0
THRESHOLD_HIGH = 50.0
NO_REUSE_CATS = ["Paint / chemicals"]
