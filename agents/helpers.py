# ---------------------------------------------------------
# Shared helper functions
# ---------------------------------------------------------

def approx_cmc(card):
    """
    Approximate converted mana cost (CMC) from card.manacost,
    which is a dict of mana symbol -> count.
    """
    cost = getattr(card, "manacost", None)
    if not cost:
        return 0
    try:
        return sum(cost.values())
    except Exception:
        return 0


def infer_mana_symbol(card):
    """
    Infer a single mana symbol for this card, based on its color.

    For mono-colored cards, this returns 'W', 'U', 'B', 'R', or 'G'.
    For colorless or missing info, falls back to '1' (generic).

    This makes our mana hack work for any mono-color deck (including blue),
    without hard-coded if/else chains.
    """
    color_char = "1"
    if hasattr(card, "characteristics"):
        colors = getattr(card.characteristics, "color", []) or []
        # colors is typically a list like ['W'], ['G'], ['U', 'R'], etc.
        if colors:
            color_char = colors[0]
    if not color_char:
        color_char = "1"
    return color_char


def get_card_name(card):
    """
    Try to get a human-readable card name.
    """
    if hasattr(card, "name"):
        return card.name
    if hasattr(card, "characteristics"):
        return getattr(card.characteristics, "name", str(card))
    return str(card)


def classify_spell_role(card):
    """
    Classify certain spells into simple roles we can reason about:
      - 'burn'      : single-target damage (Lightning Bolt, Lightning Strike)
      - 'pump'      : simple +X/+X combat trick (Giant Growth, Titanic Growth)
      - 'pacifism'  : Pacifism-style aura removal

    In your limited research pool, this is allowed to be name-based.
    """
    name = get_card_name(card)

    # Red burn
    if name in ("Lightning Bolt", "Lightning Strike"):
        return "burn"

    # Green pump
    if name in ("Giant Growth", "Titanic Growth"):
        return "pump"

    # White aura removal
    if name == "Pacifism":
        return "pacifism"

    return None
