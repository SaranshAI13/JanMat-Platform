"""
JanMat Platform — Realistic Campaign Mock Data Generator
Generates synthetic, high-fidelity political campaign feedback telemetry,
constituencies, booths, and issue escalation records for 50 constituencies across 5 states.
"""

import os
import sys
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add parent directory to path to allow importing database models
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database.models import (
    get_engine, init_db, get_session,
    Constituency, Booth, FeedbackTelemetry, IssueLog
)

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

# 50 Constituencies across 5 Key States
CONSTITUENCIES_CATALOG = [
    # Uttar Pradesh (14)
    {"id": "UP_VARANASI", "name": "Varanasi", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 3 - Stronghold", "lat": 25.3176, "lon": 82.9739, "electorate": 1820000},
    {"id": "UP_GORAKHPUR", "name": "Gorakhpur", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 3 - Stronghold", "lat": 26.7606, "lon": 83.3732, "electorate": 1950000},
    {"id": "UP_LUCKNOW", "name": "Lucknow", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 3 - Stronghold", "lat": 26.8467, "lon": 80.9462, "electorate": 2040000},
    {"id": "UP_AMETHI", "name": "Amethi", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 26.1557, "lon": 81.8122, "electorate": 1740000},
    {"id": "UP_PRAYAGRAJ", "name": "Prayagraj", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 25.4358, "lon": 81.8463, "electorate": 1890000},
    {"id": "UP_PHULPUR", "name": "Phulpur", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 25.5500, "lon": 82.0800, "electorate": 1920000},
    {"id": "UP_AYODHYA", "name": "Ayodhya (Faizabad)", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 26.7922, "lon": 82.1998, "electorate": 1850000},
    {"id": "UP_KANPUR", "name": "Kanpur Nagar", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 26.4499, "lon": 80.3319, "electorate": 1780000},
    {"id": "UP_MEERUT", "name": "Meerut", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 28.9845, "lon": 77.7064, "electorate": 1910000},
    {"id": "UP_MATHURA", "name": "Mathura", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 27.4924, "lon": 77.6737, "electorate": 1810000},
    {"id": "UP_AGRA", "name": "Agra", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 27.1767, "lon": 78.0081, "electorate": 1980000},
    {"id": "UP_BAREILLY", "name": "Bareilly", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 28.3670, "lon": 79.4304, "electorate": 1860000},
    {"id": "UP_MORADABAD", "name": "Moradabad", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 28.8386, "lon": 78.7733, "electorate": 1940000},
    {"id": "UP_AZAMGARH", "name": "Azamgarh", "state": "Uttar Pradesh", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 26.0687, "lon": 83.1844, "electorate": 1870000},

    # Maharashtra (10)
    {"id": "MH_BARAMATI", "name": "Baramati", "state": "Maharashtra", "zone": "West", "tier": "Tier 1 - Critical Battleground", "lat": 18.1519, "lon": 74.5772, "electorate": 2150000},
    {"id": "MH_NAGPUR", "name": "Nagpur", "state": "Maharashtra", "zone": "West", "tier": "Tier 3 - Stronghold", "lat": 21.1458, "lon": 79.0882, "electorate": 2160000},
    {"id": "MH_PUNE", "name": "Pune", "state": "Maharashtra", "zone": "West", "tier": "Tier 2 - Lean Favorable", "lat": 18.5204, "lon": 73.8567, "electorate": 2070000},
    {"id": "MH_NASHIK", "name": "Nashik", "state": "Maharashtra", "zone": "West", "tier": "Tier 1 - Critical Battleground", "lat": 19.9975, "lon": 73.7898, "electorate": 1960000},
    {"id": "MH_KOLHAPUR", "name": "Kolhapur", "state": "Maharashtra", "zone": "West", "tier": "Tier 1 - Critical Battleground", "lat": 16.7050, "lon": 74.2433, "electorate": 1910000},
    {"id": "MH_THANE", "name": "Thane", "state": "Maharashtra", "zone": "West", "tier": "Tier 2 - Lean Favorable", "lat": 19.2183, "lon": 72.9781, "electorate": 2390000},
    {"id": "MH_SOLAPUR", "name": "Solapur", "state": "Maharashtra", "zone": "West", "tier": "Tier 1 - Critical Battleground", "lat": 17.6599, "lon": 75.9064, "electorate": 1980000},
    {"id": "MH_AURANGABAD", "name": "Chhatrapati Sambhajinagar", "state": "Maharashtra", "zone": "West", "tier": "Tier 1 - Critical Battleground", "lat": 19.8762, "lon": 75.3433, "electorate": 1890000},
    {"id": "MH_NANDED", "name": "Nanded", "state": "Maharashtra", "zone": "West", "tier": "Tier 1 - Critical Battleground", "lat": 19.1383, "lon": 77.3210, "electorate": 1820000},
    {"id": "MH_AMRAVATI", "name": "Amravati", "state": "Maharashtra", "zone": "West", "tier": "Tier 1 - Critical Battleground", "lat": 20.9374, "lon": 77.7796, "electorate": 1830000},

    # Rajasthan (8)
    {"id": "RJ_JODHPUR", "name": "Jodhpur", "state": "Rajasthan", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 26.2389, "lon": 73.0243, "electorate": 1970000},
    {"id": "RJ_JAIPUR_RURAL", "name": "Jaipur Rural", "state": "Rajasthan", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 26.9124, "lon": 75.7873, "electorate": 2010000},
    {"id": "RJ_KOTA", "name": "Kota", "state": "Rajasthan", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 25.2138, "lon": 75.8648, "electorate": 1930000},
    {"id": "RJ_UDAIPUR", "name": "Udaipur", "state": "Rajasthan", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 24.5854, "lon": 73.7125, "electorate": 2060000},
    {"id": "RJ_BIKANER", "name": "Bikaner", "state": "Rajasthan", "zone": "North", "tier": "Tier 3 - Stronghold", "lat": 28.0229, "lon": 73.3119, "electorate": 1880000},
    {"id": "RJ_ALWAR", "name": "Alwar", "state": "Rajasthan", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 27.5530, "lon": 76.6346, "electorate": 1950000},
    {"id": "RJ_CHITTORGARH", "name": "Chittorgarh", "state": "Rajasthan", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 24.8887, "lon": 74.6269, "electorate": 2020000},
    {"id": "RJ_BARMER", "name": "Barmer", "state": "Rajasthan", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 25.7532, "lon": 71.3967, "electorate": 2180000},

    # Madhya Pradesh (10)
    {"id": "MP_INDORE", "name": "Indore", "state": "Madhya Pradesh", "zone": "Central", "tier": "Tier 3 - Stronghold", "lat": 22.7196, "lon": 75.8577, "electorate": 2350000},
    {"id": "MP_BHOPAL", "name": "Bhopal", "state": "Madhya Pradesh", "zone": "Central", "tier": "Tier 2 - Lean Favorable", "lat": 23.2599, "lon": 77.4126, "electorate": 2120000},
    {"id": "MP_GWALIOR", "name": "Gwalior", "state": "Madhya Pradesh", "zone": "Central", "tier": "Tier 1 - Critical Battleground", "lat": 26.2183, "lon": 78.1828, "electorate": 2040000},
    {"id": "MP_JABALPUR", "name": "Jabalpur", "state": "Madhya Pradesh", "zone": "Central", "tier": "Tier 2 - Lean Favorable", "lat": 23.1815, "lon": 79.9864, "electorate": 1920000},
    {"id": "MP_UJJAIN", "name": "Ujjain", "state": "Madhya Pradesh", "zone": "Central", "tier": "Tier 3 - Stronghold", "lat": 23.1765, "lon": 75.7885, "electorate": 1820000},
    {"id": "MP_SAGAR", "name": "Sagar", "state": "Madhya Pradesh", "zone": "Central", "tier": "Tier 2 - Lean Favorable", "lat": 23.8388, "lon": 78.7378, "electorate": 1710000},
    {"id": "MP_REWA", "name": "Rewa", "state": "Madhya Pradesh", "zone": "Central", "tier": "Tier 2 - Lean Favorable", "lat": 24.5362, "lon": 81.3037, "electorate": 1750000},
    {"id": "MP_CHHINDWARA", "name": "Chhindwara", "state": "Madhya Pradesh", "zone": "Central", "tier": "Tier 1 - Critical Battleground", "lat": 22.0574, "lon": 78.9382, "electorate": 1630000},
    {"id": "MP_MORENA", "name": "Morena", "state": "Madhya Pradesh", "zone": "Central", "tier": "Tier 1 - Critical Battleground", "lat": 26.4947, "lon": 77.9940, "electorate": 1890000},
    {"id": "MP_KHARGONE", "name": "Khargone", "state": "Madhya Pradesh", "zone": "Central", "tier": "Tier 2 - Lean Favorable", "lat": 21.8236, "lon": 75.6179, "electorate": 1910000},

    # Karnataka (8)
    {"id": "KA_BENGALURU_S", "name": "Bengaluru South", "state": "Karnataka", "zone": "South", "tier": "Tier 3 - Stronghold", "lat": 12.9237, "lon": 77.5838, "electorate": 2210000},
    {"id": "KA_MYSURU", "name": "Mysuru", "state": "Karnataka", "zone": "South", "tier": "Tier 1 - Critical Battleground", "lat": 12.2958, "lon": 76.6394, "electorate": 1980000},
    {"id": "KA_HUBBALLI", "name": "Dharwad (Hubballi)", "state": "Karnataka", "zone": "South", "tier": "Tier 2 - Lean Favorable", "lat": 15.3647, "lon": 75.1240, "electorate": 1780000},
    {"id": "KA_BELAGAVI", "name": "Belagavi", "state": "Karnataka", "zone": "South", "tier": "Tier 1 - Critical Battleground", "lat": 15.8497, "lon": 74.4977, "electorate": 1890000},
    {"id": "KA_SHIVAMOGGA", "name": "Shivamogga", "state": "Karnataka", "zone": "South", "tier": "Tier 2 - Lean Favorable", "lat": 13.9299, "lon": 75.5681, "electorate": 1720000},
    {"id": "KA_MANGALURU", "name": "Dakshina Kannada (Mangaluru)", "state": "Karnataka", "zone": "South", "tier": "Tier 3 - Stronghold", "lat": 12.9141, "lon": 74.8560, "electorate": 1760000},
    {"id": "KA_KALABURAGI", "name": "Kalaburagi", "state": "Karnataka", "zone": "South", "tier": "Tier 1 - Critical Battleground", "lat": 17.3297, "lon": 76.8343, "electorate": 1940000},
    {"id": "KA_DAVANAGERE", "name": "Davanagere", "state": "Karnataka", "zone": "South", "tier": "Tier 1 - Critical Battleground", "lat": 14.4644, "lon": 75.9218, "electorate": 1710000},

    # Haryana (10)
    {"id": "HR_GURUGRAM", "name": "Gurugram", "state": "Haryana", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 28.4595, "lon": 77.0266, "electorate": 2150000},
    {"id": "HR_FARIDABAD", "name": "Faridabad", "state": "Haryana", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 28.4089, "lon": 77.3178, "electorate": 1980000},
    {"id": "HR_ROHTAK", "name": "Rohtak", "state": "Haryana", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 28.8955, "lon": 76.6066, "electorate": 1750000},
    {"id": "HR_HISAR", "name": "Hisar", "state": "Haryana", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 29.1492, "lon": 75.7217, "electorate": 1680000},
    {"id": "HR_KARNAL", "name": "Karnal", "state": "Haryana", "zone": "North", "tier": "Tier 3 - Stronghold", "lat": 29.6857, "lon": 76.9905, "electorate": 1890000},
    {"id": "HR_AMBALA", "name": "Ambala", "state": "Haryana", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 30.3782, "lon": 76.7767, "electorate": 1820000},
    {"id": "HR_SONIPAT", "name": "Sonipat", "state": "Haryana", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 28.9931, "lon": 77.0151, "electorate": 1720000},
    {"id": "HR_KURUKSHETRA", "name": "Kurukshetra", "state": "Haryana", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 29.9695, "lon": 76.8783, "electorate": 1780000},
    {"id": "HR_BHIWANI", "name": "Bhiwani-Mahendragarh", "state": "Haryana", "zone": "North", "tier": "Tier 2 - Lean Favorable", "lat": 28.7932, "lon": 76.1390, "electorate": 1690000},
    {"id": "HR_SIRSA", "name": "Sirsa", "state": "Haryana", "zone": "North", "tier": "Tier 1 - Critical Battleground", "lat": 29.5349, "lon": 75.0280, "electorate": 1850000},
]

DEMOGRAPHIC_COHORTS = ["Youth", "Farmers", "Women", "Senior Citizens"]

WELFARE_SCHEMES = [
    "PM-KISAN", 
    "Ayushman Bharat", 
    "PMAY (Pradhan Mantri Awas Yojana)", 
    "Jal Jeevan Mission", 
    "PM Ujjwala Yojana", 
    "Road Infra & PMGSY"
]

ISSUE_CATEGORIES = [
    "Agriculture & Subsidies",
    "Healthcare & Hospitals",
    "Road & Rural Infrastructure",
    "Employment & Skill Development",
    "Drinking Water & Sanitation",
    "Civil Amenities & Governance"
]

# Realistic feedback templates by cohort and scheme
FEEDBACK_TEMPLATES = {
    ("Farmers", "PM-KISAN"): [
        ("PM-KISAN ₹2000 installment credited directly to bank account on time. Helped purchase rabi season fertilizers and seeds without taking private loans.", 0.88, "Positive", "Agriculture & Subsidies"),
        ("Received previous 3 installments but 16th installment blocked due to e-KYC land record mismatch at patwari office. Need quick camp.", -0.52, "Negative", "Agriculture & Subsidies"),
        ("DBT transfer is transparent and eliminated middlemen, but input costs like diesel and pesticides have increased, so benefit is offset.", 0.15, "Neutral", "Agriculture & Subsidies"),
        ("Farmer cooperative society ran out of DAP fertilizer. Standing in queues since early morning.", -0.78, "Negative", "Agriculture & Subsidies"),
        ("Solar pump subsidy under PM-KUSUM sanctioned smoothly. Irrigation electricity bill reduced to zero.", 0.92, "Positive", "Agriculture & Subsidies"),
        ("Wheat procurement at MSP center is running efficiently this season. Weighment slip received instantly via SMS.", 0.82, "Positive", "Agriculture & Subsidies"),
    ],
    ("Farmers", "Road Infra & PMGSY"): [
        ("New concrete PMGSY road connected our village to the main tehsil mandi. Tractor transport cost dropped by 40%.", 0.84, "Positive", "Road & Rural Infrastructure"),
        ("Culvert damaged during last monsoon still not repaired. Waterlogging blocks sugarcane transport to sugar mill.", -0.71, "Negative", "Road & Rural Infrastructure"),
        ("Road construction started 6 months ago but contractor left gravel unpacked. Flying dust causing crop damage along road.", -0.62, "Negative", "Road & Rural Infrastructure"),
    ],
    ("Women", "PM Ujjwala Yojana"): [
        ("Ujjwala gas connection relieved us from daily smoke in kitchen. Eye irritation stopped, cooking is much faster.", 0.89, "Positive", "Civil Amenities & Governance"),
        ("LPG connection received under Ujjwala scheme, but refill price of cylinder is difficult to afford every month without extra subsidy.", -0.34, "Negative", "Civil Amenities & Governance"),
        ("Subsidized cylinder refill booking through WhatsApp is very convenient. Delivered home within 24 hours.", 0.78, "Positive", "Civil Amenities & Governance"),
    ],
    ("Women", "PMAY (Pradhan Mantri Awas Yojana)"): [
        ("Pucca house built under PMAY registered in my name. Our family finally has dignity and a secure roof over our heads.", 0.95, "Positive", "Civil Amenities & Governance"),
        ("First installment of PMAY received and foundation completed, but second geo-tagging inspection delayed by municipal officer.", -0.48, "Negative", "Civil Amenities & Governance"),
        ("PMAY house construction finished on time. Direct bank transfer ensured zero bribery.", 0.91, "Positive", "Civil Amenities & Governance"),
    ],
    ("Women", "Jal Jeevan Mission"): [
        ("Under Har Ghar Jal, piped drinking water tap installed right inside house yard. No need to walk 1.5 km to village handpump.", 0.93, "Positive", "Drinking Water & Sanitation"),
        ("Tap water pipes laid down throughout the village lane, but water supply comes only 2 days a week for 20 minutes with low pressure.", -0.65, "Negative", "Drinking Water & Sanitation"),
        ("Piped water pipeline work completed, but contractor broke the lane pavement and did not repave it.", -0.58, "Negative", "Drinking Water & Sanitation"),
        ("Clean tap water has reduced seasonal diarrhea and stomach infections among our children.", 0.86, "Positive", "Drinking Water & Sanitation"),
    ],
    ("Senior Citizens", "Ayushman Bharat"): [
        ("Used Ayushman golden card for knee replacement and cardiac stent at empaneled medical college. Entirely cashless treatment.", 0.96, "Positive", "Healthcare & Hospitals"),
        ("Empaneled private nursing home claimed their Ayushman portal server was down and demanded ₹15,000 cash advance.", -0.82, "Negative", "Healthcare & Hospitals"),
        ("Generic medicines at Jan Aushadhi Kendra saved ₹1,200 on my monthly BP and diabetes medication.", 0.88, "Positive", "Healthcare & Hospitals"),
        ("Primary health center has doctor only twice a week. Testing lab remains closed most days.", -0.74, "Negative", "Healthcare & Hospitals"),
    ],
    ("Youth", "Employment & Skill Development"): [
        ("New PM Kaushal Vikas Kendra in district offering CNC machining and solar technician training with placement assistance.", 0.79, "Positive", "Employment & Skill Development"),
        ("Exam paper leak rumors and prolonged delay in government recruitment exams creating deep frustration among village students.", -0.86, "Negative", "Employment & Skill Development"),
        ("Industrial expressway development brought warehousing jobs in our area, local youth getting logistics work.", 0.74, "Positive", "Employment & Skill Development"),
        ("Need free government competitive coaching center and digital library at the tehsil headquarters for UPSC/SSC aspirants.", -0.30, "Neutral", "Employment & Skill Development"),
        ("Start-up India Mudra loan sanctioned for opening cyber cafe and photocopy shop without collateral.", 0.81, "Positive", "Employment & Skill Development"),
    ],
    ("Youth", "Road Infra & PMGSY"): [
        ("4-lane highway corridor cut travel time between district and state capital in half. Daily bus commuting is very easy.", 0.85, "Positive", "Road & Rural Infrastructure"),
        ("Street lights on highway bypass not functioning for 2 months, leading to motorcycle accidents at night.", -0.69, "Negative", "Road & Rural Infrastructure"),
        ("Road quality is smooth, but speed breakers needed near village school crossing to prevent speeding trucks.", -0.25, "Neutral", "Road & Rural Infrastructure"),
    ]
}

# Generic fallbacks
GENERIC_FEEDBACKS = [
    ("Local administration officers are responsive during Tehsil Diwas meetings.", 0.65, "Positive", "Civil Amenities & Governance"),
    ("Electricity supply is now stable for 18-20 hours daily compared to previous years.", 0.80, "Positive", "Civil Amenities & Governance"),
    ("Transformers burn out during summer peak load and take 4 days to replace.", -0.70, "Negative", "Civil Amenities & Governance"),
    ("Ration distribution under PMGKAY free foodgrain scheme is seamless with biometric e-POS machines.", 0.90, "Positive", "Civil Amenities & Governance"),
    ("PDS ration dealer deducting 1 kg grain per ration card citing transit loss. Need inspection.", -0.66, "Negative", "Civil Amenities & Governance"),
    ("Garbage collection van visits twice a week in ward, cleanliness has visibly improved.", 0.72, "Positive", "Civil Amenities & Governance"),
]

def generate_mock_campaign_data(
    num_feedbacks: int = 1500,
    num_issues: int = 240,
    save_to_db: bool = True
):
    """
    Generates rich, realistic campaign dataset across 50 constituencies.
    Returns dictionaries of DataFrames and saves to database/CSV.
    """
    print(f"Generating data for 50 constituencies across 5 states...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    # 1. Constituencies DataFrame
    constituencies_df = pd.DataFrame(CONSTITUENCIES_CATALOG)
    constituencies_df.rename(columns={'tier': 'priority_tier', 'lat': 'latitude', 'lon': 'longitude', 'electorate': 'electorate_size'}, inplace=True)
    constituencies_df.to_csv(os.path.join(data_dir, 'constituencies.csv'), index=False)

    # 2. Booths Generation (8 booths per constituency = 400 micro booths)
    booths_list = []
    booth_counter = 1
    coordinator_names = [
        "Ramesh Kumar", "Suresh Sharma", "Vikram Singh", "Pooja Verma", "Manoj Patil",
        "Sunita Devi", "Rajesh Deshmukh", "Anil Choudhary", "Girish Hegde", "Priyanka Patel",
        "Dinesh Yadav", "Kamla Bai", "Satish Mishra", "Basavaraj Gowda", "Arjun Meena",
        "Virender Hooda", "Baljeet Malik", "Sandeep Ahlawat", "Jaiveer Rathi", "Sunita Phogat"
    ]

    for c in CONSTITUENCIES_CATALOG:
        for b_num in range(1, 9):
            booths_list.append({
                "id": booth_counter,
                "booth_number": b_num,
                "booth_name": f"{c['name']} Ward-{b_num} Govt School Polling Booth",
                "constituency_id": c["id"],
                "coordinator_name": random.choice(coordinator_names),
                "coordinator_phone": f"+91 {random.randint(91000, 99999)} {random.randint(10000, 99999)}",
                "total_registered_voters": random.randint(850, 1450)
            })
            booth_counter += 1

    booths_df = pd.DataFrame(booths_list)
    booths_df.to_csv(os.path.join(data_dir, 'booths.csv'), index=False)

    # 3. Feedback Telemetry Generation
    # Simulation spans the last 30 days. We model a progressive reduction in operational lag
    # from ~48 hours down to ~27 hours (showing telemetry impact).
    start_date = datetime.now() - timedelta(days=30)
    feedbacks_list = []

    # Map booth IDs to their constituency
    booth_map = {b["id"]: b["constituency_id"] for b in booths_list}

    for i in range(1, num_feedbacks + 1):
        booth = random.choice(booths_list)
        b_id = booth["id"]
        c_id = booth["constituency_id"]

        # Date distribution: more recent records
        day_offset = int(np.random.beta(2, 1) * 30) # Biased towards recent days
        feedback_date = start_date + timedelta(days=day_offset, hours=random.randint(0, 23), minutes=random.randint(0, 59))

        cohort = random.choice(DEMOGRAPHIC_COHORTS)
        scheme = random.choice(WELFARE_SCHEMES)

        # Lookup feedback template
        template_pool = FEEDBACK_TEMPLATES.get((cohort, scheme))
        if not template_pool:
            # Fallback to scheme match or generic
            matching_keys = [k for k in FEEDBACK_TEMPLATES.keys() if k[1] == scheme or k[0] == cohort]
            if matching_keys:
                template_pool = FEEDBACK_TEMPLATES[random.choice(matching_keys)]
            else:
                template_pool = GENERIC_FEEDBACKS

        text, base_sentiment, base_label, category = random.choice(template_pool)

        # Add small random jitter to sentiment score (-0.05 to +0.05)
        sentiment_score = round(float(np.clip(base_sentiment + random.uniform(-0.06, 0.06), -1.0, 1.0)), 2)
        if sentiment_score >= 0.20:
            sentiment_label = "Positive"
        elif sentiment_score <= -0.20:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        # Model operational reporting lag reduction:
        # Older records (day 0-10) had baseline ~48h lag
        # Recent records (day 20-30) reduced to ~27h lag (-40% telemetry breakthrough)
        progress_ratio = day_offset / 30.0 # 0.0 to 1.0
        expected_lag = 48.0 - (progress_ratio * 20.0) # 48.0h down to 28.0h
        reporting_lag = round(float(max(4.0, np.random.normal(expected_lag, 5.5))), 1)

        is_offline = random.random() < 0.35 # 35% offline captured

        feedbacks_list.append({
            "id": i,
            "constituency_id": c_id,
            "booth_id": b_id,
            "demographic_cohort": cohort,
            "welfare_scheme_mentioned": scheme,
            "citizen_feedback_text": text,
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "issue_category": category,
            "reporting_lag_hours": reporting_lag,
            "is_offline_captured": is_offline,
            "reporting_timestamp": feedback_date
        })

    feedbacks_df = pd.DataFrame(feedbacks_list)
    feedbacks_df.sort_values(by="reporting_timestamp", inplace=True)
    feedbacks_df.to_csv(os.path.join(data_dir, 'feedback_telemetry.csv'), index=False)

    # 4. Issue Escalation Logs
    # P0/Critical issues must show <24h SLA compliance tracking
    issues_list = []
    priorities = ["P0 - Critical", "P1 - High", "P2 - Medium", "P3 - Low"]
    priority_weights = [0.18, 0.32, 0.35, 0.15]
    statuses = ["Reported", "In Progress", "Resolved"]

    issue_titles = [
        ("Fertilizer Shortage at Cooperative Mandi", "Agriculture & Subsidies"),
        ("Ayushman Card Rejection by Empaneled Hospital", "Healthcare & Hospitals"),
        ("Damaged Culvert / Potholes Halting Sugarcane Transit", "Road & Rural Infrastructure"),
        ("Drinking Water Pipeline Disruption in Harijan Basti", "Drinking Water & Sanitation"),
        ("Transformer Burnout Causing 72hr Blackout", "Civil Amenities & Governance"),
        ("PDS Fair Price Shop Biometric Failure", "Civil Amenities & Governance"),
        ("Aspirants Protest Delayed Sub-Inspector Exam Result", "Employment & Skill Development"),
        ("PM-KISAN Installment Blocked Due to e-KYC Portal Glitch", "Agriculture & Subsidies"),
        ("PMAY Geo-tagging Blocked by Block Development Clerk", "Civil Amenities & Governance"),
        ("Primary Health Center Doctor Absent on Weekly OPD Day", "Healthcare & Hospitals")
    ]

    for j in range(1, num_issues + 1):
        booth = random.choice(booths_list)
        b_id = booth["id"]
        c_id = booth["constituency_id"]

        title, category = random.choice(issue_titles)
        priority = random.choices(priorities, weights=priority_weights)[0]

        # Timestamp in last 20 days
        days_ago = random.randint(1, 20)
        hours_ago = random.randint(1, 23)
        reported_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

        # Status and SLA resolution logic
        if days_ago > 5:
            # Older issues mostly resolved
            status = random.choices(statuses, weights=[0.10, 0.15, 0.75])[0]
        else:
            # Recent issues active
            status = random.choices(statuses, weights=[0.40, 0.40, 0.20])[0]

        resolved_at = None
        sla_breached = False
        notes = None

        if status == "Resolved":
            # P0 target < 24h
            if priority == "P0 - Critical":
                # 85% resolved within 24h SLA!
                if random.random() < 0.85:
                    hours_to_resolve = random.uniform(8.0, 22.5)
                    sla_breached = False
                else:
                    hours_to_resolve = random.uniform(25.0, 42.0)
                    sla_breached = True
            else:
                hours_to_resolve = random.uniform(12.0, 54.0)
                sla_breached = hours_to_resolve > 48.0

            resolved_at = reported_at + timedelta(hours=hours_to_resolve)
            notes = f"Intervention executed by District Taskforce. Field team verified with booth coordinator {booth['coordinator_name']}."
        elif status == "In Progress":
            hours_open = (datetime.now() - reported_at).total_seconds() / 3600.0
            sla_breached = (priority == "P0 - Critical" and hours_open > 24.0)
            notes = "Case escalated to Sub-Divisional Magistrate (SDM) / Executive Engineer. Awaiting field compliance report."
        else:
            hours_open = (datetime.now() - reported_at).total_seconds() / 3600.0
            sla_breached = (priority == "P0 - Critical" and hours_open > 24.0)
            notes = "Grievance ticket logged by Booth Coordinator via JanMat offline sync."

        ticket_code = f"JM-{c_id.split('_')[0]}-{c_id.split('_')[-1][:3]}-{1000 + j}"

        issues_list.append({
            "id": j,
            "ticket_id": ticket_code,
            "constituency_id": c_id,
            "booth_id": b_id,
            "title": f"{title} (Booth {booth['booth_number']})",
            "description": f"Field report from {booth['booth_name']}: {title}. Urgent intervention requested for 200+ affected households.",
            "issue_category": category,
            "priority": priority,
            "status": status,
            "assigned_to": random.choice(["District Campaign Cell", "Mandal In-Charge", "State War Room Rapid Response", "Local MLA Liaison"]),
            "sla_hours_limit": 24.0 if priority == "P0 - Critical" else 48.0,
            "reported_at": reported_at,
            "resolved_at": resolved_at,
            "resolution_notes": notes,
            "sla_breached": sla_breached
        })

    issues_df = pd.DataFrame(issues_list)
    issues_df.sort_values(by="reported_at", ascending=False, inplace=True)
    issues_df.to_csv(os.path.join(data_dir, 'issues_log.csv'), index=False)

    print(f"CSVs generated in {data_dir}:")
    print(f"  - Constituencies: {len(constituencies_df)} rows")
    print(f"  - Booths: {len(booths_df)} rows")
    print(f"  - Feedback Telemetry: {len(feedbacks_df)} rows")
    print(f"  - Issues Log: {len(issues_df)} rows")

    # 5. Populate SQLite Database
    if save_to_db:
        print("Populating SQLite database via SQLAlchemy ORM...")
        db_path = os.path.join(data_dir, 'janmat.db')
        engine = get_engine(db_path)
        init_db(engine)
        session = get_session(engine)

        try:
            # Clear existing data if present
            session.query(IssueLog).delete()
            session.query(FeedbackTelemetry).delete()
            session.query(Booth).delete()
            session.query(Constituency).delete()
            session.commit()

            # Insert Constituencies
            for _, r in constituencies_df.iterrows():
                session.add(Constituency(
                    id=r["id"],
                    name=r["name"],
                    state=r["state"],
                    zone=r["zone"],
                    priority_tier=r["priority_tier"],
                    electorate_size=int(r["electorate_size"]),
                    latitude=float(r["latitude"]),
                    longitude=float(r["longitude"])
                ))
            session.commit()

            # Insert Booths
            for _, r in booths_df.iterrows():
                session.add(Booth(
                    id=int(r["id"]),
                    booth_number=int(r["booth_number"]),
                    booth_name=r["booth_name"],
                    constituency_id=r["constituency_id"],
                    coordinator_name=r["coordinator_name"],
                    coordinator_phone=r["coordinator_phone"],
                    total_registered_voters=int(r["total_registered_voters"])
                ))
            session.commit()

            # Insert Feedback Telemetry
            for _, r in feedbacks_df.iterrows():
                session.add(FeedbackTelemetry(
                    id=int(r["id"]),
                    constituency_id=r["constituency_id"],
                    booth_id=int(r["booth_id"]),
                    demographic_cohort=r["demographic_cohort"],
                    welfare_scheme_mentioned=r["welfare_scheme_mentioned"],
                    citizen_feedback_text=r["citizen_feedback_text"],
                    sentiment_score=float(r["sentiment_score"]),
                    sentiment_label=r["sentiment_label"],
                    issue_category=r["issue_category"],
                    reporting_lag_hours=float(r["reporting_lag_hours"]),
                    is_offline_captured=bool(r["is_offline_captured"]),
                    reporting_timestamp=pd.to_datetime(r["reporting_timestamp"]).to_pydatetime()
                ))
            session.commit()

            # Insert Issues Log
            for _, r in issues_df.iterrows():
                resolved_dt = pd.to_datetime(r["resolved_at"]).to_pydatetime() if pd.notna(r["resolved_at"]) else None
                session.add(IssueLog(
                    id=int(r["id"]),
                    ticket_id=r["ticket_id"],
                    constituency_id=r["constituency_id"],
                    booth_id=int(r["booth_id"]),
                    title=r["title"],
                    description=r["description"],
                    issue_category=r["issue_category"],
                    priority=r["priority"],
                    status=r["status"],
                    assigned_to=r["assigned_to"],
                    sla_hours_limit=float(r["sla_hours_limit"]),
                    reported_at=pd.to_datetime(r["reported_at"]).to_pydatetime(),
                    resolved_at=resolved_dt,
                    resolution_notes=r["resolution_notes"],
                    sla_breached=bool(r["sla_breached"])
                ))
            session.commit()
            print("SQLite database populated successfully at:", db_path)

        except Exception as e:
            session.rollback()
            print(f"Error populating database: {e}")
            raise e
        finally:
            session.close()

    return {
        "constituencies": constituencies_df,
        "booths": booths_df,
        "feedback": feedbacks_df,
        "issues": issues_df
    }

if __name__ == "__main__":
    generate_mock_campaign_data(num_feedbacks=2400, num_issues=380)
