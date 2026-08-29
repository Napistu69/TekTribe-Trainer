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


def generate_color_regions() -> dict:
    """Generate default wild-type color regions (no mutations on first hatch)."""
    return {
        "base": {"region": "base", "base_color": "#808080", "mutated_color": None, "mutation_tier": None},
        "pattern": {"region": "pattern", "base_color": "#606060", "mutated_color": None, "mutation_tier": None},
        "accent": {"region": "accent", "base_color": "#707070", "mutated_color": None, "mutation_tier": None},
        "eye_glow": {"region": "eye_glow", "base_color": "#00ffcc", "mutated_color": None, "mutation_tier": None},
        "intensity": {"region": "intensity", "base_color": "#808080", "mutated_color": None, "mutation_tier": None},
    }
