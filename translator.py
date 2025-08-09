def genz_to_python(genz_code):
    # Very basic slang-to-Python mapping
    slang_dict = {
        "say": "print",
        "vibe": "for",
        "snacc": "in",
        "nums": "range",
        "sus": "if",
        "nope": "else",
        "fr": "True",
        "cap": "False",
        "maths": "+",
        "minus": "-",
        "times": "*",
        "div": "/",
    }

    python_code = genz_code
    for slang, py in slang_dict.items():
        python_code = python_code.replace(slang, py)

    return python_code
