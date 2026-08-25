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


def generate_base_stats(species: str) -> dict:
    """Generate base stats for a creature based on species.
    
    Returns game-adjacent stats: health, stamina, strength, speed, intelligence, imprint_affinity.
    """
    # Species-specific base stat templates
    templates = {
        "parasaur": {"health": 100, "stamina": 80, "strength": 60, "speed": 70, "intelligence": 75, "imprint_affinity": 90},
        "dilo": {"health": 70, "stamina": 90, "strength": 50, "speed": 85, "intelligence": 80, "imprint_affinity": 70},
        "trike": {"health": 150, "stamina": 70, "strength": 110, "speed": 50, "intelligence": 60, "imprint_affinity": 80},
        "ptera": {"health": 60, "stamina": 120, "strength": 40, "speed": 130, "intelligence": 85, "imprint_affinity": 65},
        "raptor": {"health": 90, "stamina": 100, "strength": 100, "speed": 120, "intelligence": 95, "imprint_affinity": 60},
        "rex": {"health": 200, "stamina": 90, "strength": 150, "speed": 80, "intelligence": 90, "imprint_affinity": 85},
    }
    return templates.get(species, {"health": 100, "stamina": 100, "strength": 100, "speed": 100, "intelligence": 100, "imprint_affinity": 50})


def generate_personality(species: str) -> tuple[str, list[str], list[str]]:
    """Generate personality for a creature based on species.
    
    Returns: (personality_type, personality_traits, behavioral_quirks)
    """
    personalities = {
        "parasaur": ("gentle", ["social", "reassuring"], ["nuzzles when happy", "gentle tail sway"]),
        "dilo": ("mischievous", ["alert", "clingy"], ["head bobs excitedly", "frill flare when startled"]),
        "trike": ("loyal", ["stubborn", "protective"], ["proud snort", "horn tilt when curious"]),
        "ptera": ("curious", ["restless", "playful"], ["perch bounce", "wing flutter when excited"]),
        "raptor": ("fierce", ["proud", "hyper_attentive"], ["pounce loop", "sharp chirp"]),
        "rex": ("intense", ["regal", "deeply_imprinting"], ["tiny roar", "chest puff"]),
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
