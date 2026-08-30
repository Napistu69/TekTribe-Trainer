"""Genetics service — generates hidden genetic potential and base stats."""
import secrets
from typing import Optional

from app.services.egg_service import CREATURES


async def generate_hidden_potential() -> float:
    """Generate a random hidden genetic potential (0.0 to 1.0).
    
    This value is SERVER-SIDE ONLY and is NEVER sent to the client.
    It affects mutation probability and latent trait expression.
    """
    # Use crypto-secure random for fairness
    return secrets.randbelow(10000) / 10000.0


def generate_biological_sex() -> str:
    """Generate random biological sex (male or female)."""
    return "male" if secrets.randbelow(2) == 0 else "female"


def generate_base_stats(species: str) -> dict:
    """Generate base stats for a creature based on species.
    
    Returns game-adjacent stats: health, stamina, strength, speed, intelligence, affinity.
    """
    # Species-specific base stat templates
    templates = {
        "parasaur": {"health": 100, "stamina": 80, "strength": 60, "speed": 70, "intelligence": 75, "affinity": 90},
        "dilo": {"health": 70, "stamina": 90, "strength": 50, "speed": 85, "intelligence": 80, "affinity": 70},
        "dodo": {"health": 60, "stamina": 60, "strength": 30, "speed": 50, "intelligence": 40, "affinity": 95},
        "trike": {"health": 150, "stamina": 70, "strength": 110, "speed": 50, "intelligence": 60, "affinity": 80},
        "ptera": {"health": 60, "stamina": 120, "strength": 40, "speed": 130, "intelligence": 85, "affinity": 65},
        "raptor": {"health": 90, "stamina": 100, "strength": 100, "speed": 120, "intelligence": 95, "affinity": 60},
        "stego": {"health": 180, "stamina": 60, "strength": 90, "speed": 40, "intelligence": 55, "affinity": 75},
        "carno": {"health": 140, "stamina": 80, "strength": 130, "speed": 90, "intelligence": 70, "affinity": 50},
        "ankylo": {"health": 200, "stamina": 50, "strength": 140, "speed": 30, "intelligence": 50, "affinity": 70},
        "argent": {"health": 130, "stamina": 140, "strength": 90, "speed": 150, "intelligence": 90, "affinity": 75},
        "allo": {"health": 110, "stamina": 110, "strength": 110, "speed": 110, "intelligence": 85, "affinity": 65},
        "mantis": {"health": 80, "stamina": 100, "strength": 120, "speed": 100, "intelligence": 95, "affinity": 45},
        "rex": {"health": 200, "stamina": 90, "strength": 150, "speed": 80, "intelligence": 90, "affinity": 85},
        "spino": {"health": 180, "stamina": 100, "strength": 140, "speed": 90, "intelligence": 85, "affinity": 80},
    }
    return templates.get(species, {"health": 100, "stamina": 100, "strength": 100, "speed": 100, "intelligence": 100, "affinity": 50})


def generate_personality(species: str) -> tuple[str, list[str], list[str]]:
    """Generate personality for a creature based on species.
    
    Returns: (personality_type, personality_traits, behavioral_quirks)
    """
    personalities = {
        "parasaur": ("gentle", ["social", "reassuring"], ["nuzzles when happy", "gentle tail sway"]),
        "dilo": ("mischievous", ["alert", "clingy"], ["head bobs excitedly", "frill flare when startled"]),
        "dodo": ("docile", ["curious", "clumsy"], ["happy flap", "peck ground rhythmically"]),
        "trike": ("loyal", ["stubborn", "protective"], ["proud snort", "horn tilt when curious"]),
        "ptera": ("curious", ["restless", "playful"], ["perch bounce", "wing flutter when excited"]),
        "raptor": ("fierce", ["proud", "hyper_attentive"], ["pounce loop", "sharp chirp"]),
        "stego": ("stoic", ["unyielding", "gentle_giant"], ["tail sway", "contented rumble"]),
        "carno": ("aggressive", ["territorial", "patient"], ["jaw snap", "low growl"]),
        "ankylo": ("unshakeable", ["deliberate", "resourceful"], ["tail club ground", "slow blink"]),
        "argent": ("majestic", ["aloof", "proud"], ["soar circle", "screech call"]),
        "allo": ("cunning", ["coordinated", "relentless"], ["pack howl", "coordinated stalk"]),
        "mantis": ("patient", ["precise", "alien"], ["foreleg tap", "head tilt"]),
        "rex": ("intense", ["regal", "deeply_imprinting"], ["tiny roar", "chest puff"]),
        "spino": ("dominant", ["aquatic", "patient_ambusher"], ["water splash", "jaw snap"]),
    }
    return personalities.get(species, ("neutral", ["curious"], ["observant"]))


def generate_color_regions(species: str = None) -> dict:
    """Generate color regions for a creature based on species.
    
    Uses species-specific region templates with random natural color IDs.
    Regions marked as 'unused' get null values.
    """
    import json
    from pathlib import Path
    
    # Load color region templates
    regions_path = Path(__file__).parent.parent / "data" / "color_regions.json"
    try:
        with open(regions_path) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to default gray regions
        return _default_color_regions()
    
    species_data = data.get("species", {}).get(species, {})
    regions = species_data.get("regions", {})
    
    result = {}
    for region_id, region_info in regions.items():
        color_id = region_info.get("color_id")
        if color_id is None:
            # Unused region
            result[region_id] = {
                "name": region_info.get("name", "unused"),
                "color_id": None,
                "color_name": None,
                "hex": None,
            }
        else:
            hex_color = _color_id_to_hex(color_id)
            result[region_id] = {
                "name": region_info.get("name", region_id),
                "color_id": color_id,
                "color_name": region_info.get("color", _get_color_name(color_id)),
                "hex": hex_color,
            }
    
    return result


def _default_color_regions() -> dict:
    """Fallback color regions (all gray)."""
    return {
        "R0": {"name": "Body", "color_id": 36, "color_name": "Light Grey", "hex": "#808080"},
        "R1": {"name": "Face", "color_id": 36, "color_name": "Light Grey", "hex": "#808080"},
        "R2": {"name": "Beak", "color_id": 36, "color_name": "Light Grey", "hex": "#808080"},
        "R3": {"name": "Forehead, Neck and Feet", "color_id": 36, "color_name": "Light Grey", "hex": "#808080"},
        "R4": {"name": "Head", "color_id": 36, "color_name": "Light Grey", "hex": "#808080"},
        "R5": {"name": "Wings and Patterning", "color_id": 36, "color_name": "Light Grey", "hex": "#808080"},
    }


def _color_id_to_hex(color_id: int) -> str:
    """Convert ARK color ID to hex color."""
    color_map = {
        8: "#D3D3D3", 14: "#4A4A4A", 17: "#A0A0A0", 21: "#FFB6C1",
        22: "#C0C0C0", 23: "#C5D5A1", 24: "#5A5A5A", 30: "#D8BFD8",
        31: "#6A6A6A", 32: "#D2B48C", 33: "#8B4513", 34: "#654321",
        35: "#3D2B1F", 36: "#808080", 37: "#F5F5DC", 38: "#FFDAB9",
        39: "#DEB887", 40: "#A9A9A9", 41: "#696969", 42: "#A0522D",
        43: "#CD853F", 49: "#DDA0DD", 51: "#B0B0B0", 52: "#909090",
        56: "#4A3C28", 62: "#5A5A5A", 63: "#888888", 64: "#AAAAAA",
        65: "#787878", 71: "#8B1A1A", 74: "#FF8C00", 75: "#FF7F50",
        76: "#FF6347", 77: "#5C4033", 78: "#4A3728", 80: "#BEBEBE",
        81: "#9E9E9E", 82: "#8A8A8A", 96: "#3C3C3C", 97: "#4F4F4F",
        98: "#5C5C5C", 99: "#696969", 100: "#FFFAF0",
    }
    return color_map.get(color_id, "#808080")


def _get_color_name(color_id: int) -> str:
    """Get color name from ARK color ID."""
    names = {
        8: "Light Grey", 14: "Dark Muted", 17: "Light All", 21: "Pale Pink",
        22: "Light All", 23: "Light Greenish Beige", 24: "Dark Muted",
        30: "Light Purple", 31: "Dark Muted", 32: "Light Tan", 33: "Medium Brown",
        34: "Dark Brown", 35: "Very Dark Brown", 36: "Light Grey", 37: "Pale Beige",
        38: "Light Pinkish Beige", 39: "Light Tan", 40: "Medium Grey",
        41: "Dark Grey", 42: "Medium Brown", 43: "Light Brown",
        49: "Light Purple", 51: "Light All", 52: "Light All", 56: "Dark Brown",
        62: "Dark Grey", 63: "Medium Grey", 64: "Light Grey", 65: "Medium Grey",
        71: "Dark Red-Brown", 74: "Orange", 75: "Orange", 76: "Orange",
        77: "Dark Brown", 78: "Dark Brown", 80: "Light Grey", 81: "Medium Grey",
        82: "Medium Grey", 96: "Dark Muted", 97: "Dark Muted", 98: "Dark Muted",
        99: "Dark Muted", 100: "Pale Off-White",
    }
    return names.get(color_id, "Unknown")
