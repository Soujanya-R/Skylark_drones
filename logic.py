from datetime import datetime, timedelta

# ---------- Helper: Check date overlap ----------
def check_date_overlap(start1, end1, start2, end2):
    return start1 <= end2 and end1 >= start2

# ---------- Find Available Pilots ----------
def find_available_pilots(pilots_df):
    return pilots_df[pilots_df["status"] == "Available"]

# ---------- Match Pilots to a Mission ----------
def match_pilots_to_mission(pilots_df, mission):
    warnings = []
    mission_start = datetime.strptime(mission["start_date"], "%Y-%m-%d")
    mission_end = datetime.strptime(mission["end_date"], "%Y-%m-%d")
    mission_skills = set([s.strip() for s in mission["required_skills"].split(",")])
    mission_certs = set([c.strip() for c in mission["required_certs"].split(",")])
    budget = mission["mission_budget_inr"]
    location = mission["location"]

    matches = []

    for _, pilot in pilots_df.iterrows():
        pilot_skills = set([s.strip() for s in pilot["skills"].split(",")])
        pilot_certs = set([c.strip() for c in pilot["certifications"].split(",")])
        pilot_available_from = datetime.strptime(pilot["available_from"], "%Y-%m-%d")
        pilot_cost = pilot["daily_rate_inr"] * ((mission_end - mission_start).days + 1)

        # Initialize mismatch flags
        mismatch = []

        if not mission_skills.issubset(pilot_skills):
            mismatch.append("Skill Mismatch")
        if not mission_certs.issubset(pilot_certs):
            mismatch.append("Certification Mismatch")
        if pilot["status"] != "Available":
            mismatch.append(f"Status: {pilot['status']}")
        if pilot_available_from > mission_start:
            mismatch.append("Not Available Yet")
        if pilot["location"] != location:
            mismatch.append("Location Mismatch")
        if pilot_cost > budget:
            mismatch.append("Exceeds Budget")

        if mismatch:
            warnings.append({"Pilot": pilot["name"], "Warnings": ", ".join(mismatch)})
        else:
            matches.append(pilot)

    return matches, warnings

# ---------- Match Drones to a Mission ----------
def match_drones_to_mission(drones_df, mission):
    warnings = []
    mission_start = datetime.strptime(mission["start_date"], "%Y-%m-%d")
    mission_end = datetime.strptime(mission["end_date"], "%Y-%m-%d")
    required_capability = mission["required_skills"]  # Assume skill maps to drone capability
    weather = mission["weather_forecast"]
    location = mission["location"]

    available_drones = []

    for _, drone in drones_df.iterrows():
        drone_caps = set([c.strip() for c in drone["capabilities"].split(",")])
        mismatch = []

        if required_capability not in drone_caps:
            mismatch.append("Capability Mismatch")
        if drone["status"] != "Available":
            mismatch.append(f"Drone Status: {drone['status']}")
        if drone["location"] != location:
            mismatch.append("Location Mismatch")
        # Weather check
        if weather.lower() == "rainy" and ("IP43" not in str(drone["weather_resistance"])):
            mismatch.append("Not Rainproof")

        if mismatch:
            warnings.append({"Drone": drone["drone_id"], "Warnings": ", ".join(mismatch)})
        else:
            available_drones.append(drone)

    return available_drones, warnings

# ---------- Urgent Reassignment ----------
def urgent_reassignment_to_mission(pilots_df, drones_df, mission):
    mission_start = datetime.strptime(mission["start_date"], "%Y-%m-%d")
    mission_end = datetime.strptime(mission["end_date"], "%Y-%m-%d")
    location = mission["location"]
    required_skills = set([s.strip() for s in mission["required_skills"].split(",")])
    required_certs = set([c.strip() for c in mission["required_certs"].split(",")])
    budget = mission["mission_budget_inr"]

    candidates = []

    for _, pilot in pilots_df.iterrows():
        pilot_skills = set([s.strip() for s in pilot["skills"].split(",")])
        pilot_certs = set([c.strip() for c in pilot["certifications"].split(",")])
        pilot_available_from = datetime.strptime(pilot["available_from"], "%Y-%m-%d")
        pilot_cost = pilot["daily_rate_inr"] * ((mission_end - mission_start).days + 1)

        # Skip if fully unavailable (e.g., location mismatch)
        if pilot["location"] != location:
            continue

        mismatch = []
        if not required_skills.issubset(pilot_skills):
            mismatch.append("Skill Mismatch")
        if not required_certs.issubset(pilot_certs):
            mismatch.append("Certification Mismatch")
        if pilot_cost > budget:
            mismatch.append("Exceeds Budget")
        if pilot_available_from > mission_start:
            mismatch.append("Not Available Yet")

        if mismatch:
            candidates.append({
                "Pilot": pilot["name"],
                "Current Status": pilot["status"],
                "Current Assignment": pilot["current_assignment"],
                "Warnings": ", ".join(mismatch)
            })

    available_drones, drone_warnings = match_drones_to_mission(drones_df, mission)

    return candidates, available_drones, drone_warnings
