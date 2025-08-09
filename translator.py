# translator.py

def genz_to_python(genz_code: str) -> str:
    slang_dict = {
        # Control flow
        "sus": "if",
        "nope": "else",
        "sus_else": "elif",
        "loop": "while",
        "vibe": "for",
        "snacc": "in",
        "stop_it": "break",
        "skip_it": "continue",
        "pass_it": "pass",

        # Functions & Classes
        "make": "def",
        "gang": "class",
        "return_it": "return",
        "bring": "import",
        "bring_as": "as",
        "from_place": "from",
        
        # Printing / Input
        "say": "print",
        "spill": "input",
        
        # Boolean
        "fr": "True",
        "cap": "False",
        "null": "None",
        "andalso": "and",
        "orelse": "or",
        "nah": "not",
        
        # Operators
        "maths": "+",
        "minus": "-",
        "times": "*",
        "div": "/",
        "modu": "%",
        "powah": "**",
        "is_same": "==",
        "not_same": "!=",
        "big": ">",
        "small": "<",
        "big_o_equal": ">=",
        "small_o_equal": "<=",
        
        # Loops utils
        "nums": "range",
        "length": "len",
        "add_it": "append",
        "pop_it": "pop",

        # Data structures
        "listy": "list",
        "dicty": "dict",
        "setty": "set",
        "tupley": "tuple",
        
        # With context manager
        "wit": "with",
        "as_it": "as",
        
        # Try / Except
        "try_it": "try",
        "catch_it": "except",
        "finally_it": "finally",
        "raise_it": "raise",
        
        # Misc
        "lambda_it": "lambda",
        "global_it": "global",
        "nonlocal_it": "nonlocal",
        "assert_it": "assert",
        "del_it": "del",
        "yield_it": "yield",
    }

    python_code = genz_code
    for slang, py in slang_dict.items():
        python_code = python_code.replace(slang, py)
    return python_code


# Alias so app.py can import it directly
def translate_to_python(genz_code: str) -> str:
    return genz_to_python(genz_code)
