def translate_error_to_genz(error_message):
    slang_map = {
        "SyntaxError": "Yo fam, that syntax is whack 💀 — fix your vibes (check colons, commas).",
        "IndentationError": "Bro, your indents are looking sus 😤 — align them properly.",
        "NameError": "Fr? You calling a homie that doesn’t even exist 🫠.",
        "TypeError": "Mismatched vibes fam — wrong type of data.",
        "ZeroDivisionError": "Bestie, you can’t flex by dividing by zero 💀.",
        "IndexError": "Yo, you tried to snacc outside the bag (list index out of range).",
        "KeyError": "Bruh, that key ain’t in the dictionary fam.",
        "AttributeError": "Chief, that object doesn’t know that move 🤷.",
        "ValueError": "Those vibes ain’t valid fam (check your values)."
    }

    for keyword, slang in slang_map.items():
        if keyword in error_message:
            return slang

    return f"Lowkey can't decode this error rn 🤔: {error_message}"
