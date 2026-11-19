"""Module - Learning Portals catalog (MOOCs, coding practice, certifications, etc.)."""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
with open(os.path.join(DATA_DIR, "learning_portals.json")) as f:
    PORTALS = json.load(f)


def get_learning_portals() -> dict:
    return {"categories": PORTALS}
