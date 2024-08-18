from utils import get_ready_to_parse_data

def tokenize_data(data):
    section_starter = ["{", "["]
    section_ender = ["}", "]"]
    seperator = [":", ","]

    def tokenize(string): 
        if string == "": return []
        tkn_lst = []

        # check for string
        if "\"" in string:
            first_quote_index = string.index("\"")
            sub_string_one = string[0: first_quote_index]
            for tkn in tokenize(sub_string_one):
                tkn_lst.append(tkn)
            if "\"" in string[first_quote_index + 1:]:
                second_quote_index = first_quote_index + string[first_quote_index + 1:].index("\"") + 1
                tkn_lst.append(string[first_quote_index: second_quote_index + 1])
                if second_quote_index + 1 < len(string):
                    sub_string_two = string[second_quote_index + 1:]
                    for tkn in tokenize(sub_string_two):
                        tkn_lst.append(tkn)
            else:
                tkn_lst.append(string[first_quote_index:])
            return tkn_lst

        # check for section delimiters
        for indicator in section_starter + section_ender + seperator:
            if indicator in string:
                # initial split
                tkns = string.split(indicator)
                # sub_token__1
                sub_tkns = tokenize(tkns[0])
                for sbtkn in sub_tkns:
                    tkn_lst.append(sbtkn)
                tkn_lst.append(indicator)
                # sub_token__2
                sub_tkns = tokenize(tkns[-1])
                for sbtkn in sub_tkns:
                    tkn_lst.append(sbtkn)
                return tkn_lst
        return [string]

    ready_to_tokenize = get_ready_to_parse_data(data).split()
    tokens = []
    for string in ready_to_tokenize:
        for tkn in tokenize(string):
            tokens.append(tkn)
    return tokens

def is_number(data):
    try:
        float(data)
    except Exception:
        return False
    return True

def is_valid_json(data):
    section_starter = ["{", "["]
    section_ender = ["}", "]"]
    
    tokens = tokenize_data(data)
    # basic invalid cases
    if len(tokens) == 0 or (tokens[0] not in section_starter) or (tokens[-1] not in section_ender) or section_ender.index(tokens[-1]) != section_starter.index(tokens[0]): return False

    # lexical characteristic
    # 1 => object
    # 2 => array
    lex_char = 1 if tokens[0] == "{" else 2
    stack = []
    statement = []
    is_comma = False
    i = 1
    while i < len(tokens) - 1:
        tkn = tokens[i]
        # in object
        if lex_char == 1:

            # string detection
            if tkn[0] == "'":
                return False
            elif tkn[0] == "\"":
                if tkn[-1] != "\"":
                    return False
                if len(statement) == 0:
                    is_comma = False
                    statement.append(tkn)
                elif statement[-1] == ":":
                    statement.append(tkn)
                else:
                    return False

            # seperator detection
            elif tkn == ":":
                if len(statement) != 1:
                    return False
                statement.append(tkn)
            elif tkn == ",":
                if len(statement) != 3:
                    return False
                statement = []
                is_comma = True

            # section detection
            elif tkn in section_starter:
                if not len(statement) or statement[-1] != ":":
                    return False
                statement.append(True)
                layer_stack_height = len(stack)
                for j in range(i, len(tokens)):
                    if tokens[j] in section_starter:
                        stack.append(section_ender[section_starter.index(tokens[j])])
                    elif tokens[j] in section_ender:
                        if len(stack) == 0 or stack[-1] != tokens[j]:
                            return False
                        stack.pop()
                        if len(stack) == layer_stack_height:
                            if not is_valid_json(" ".join(tokens[i: j + 1])):
                                return False
                            i = j
                            break
            elif tkn in section_ender:
                if len(stack) == 0 or stack[-1] != tkn:
                    return False
                stack.pop()

            # boolean and number
            elif tkn == "true" or tkn == "false" or tkn == "null"  or is_number(tkn):
                if len(statement) != 2:
                    return False
                statement.append(tkn)
            else:
                return False
        
        # in array
        else:
            # string detection
            if tkn[0] == "'":
                return False
            elif tkn[0] == "\"":
                if tkn[-1] != "\"":
                    return False
                if len(statement) == 0:
                    is_comma = False
                    statement.append(tkn)
                else:
                    return False

            # seperator detection
            elif tkn == ":":
                return False
            elif tkn == ",":
                if len(statement) != 1:
                    return False
                statement = []
                is_comma = True

            # section detection
            elif tkn in section_starter:
                statement.append(True)
                layer_stack_height = len(stack)
                stack.append(section_ender[section_starter.index(tkn)])
                for j in range(i, len(tokens)):
                    if tokens[j] in section_starter:
                        stack.append(section_ender[section_starter.index(tkn)])
                    elif tkn in section_ender:
                        if len(stack) == 0 or stack[-1] != tkn:
                            return False
                        stack.pop()
                        if len(stack) == layer_stack_height:
                            if not is_valid_json(" ".join(tokens[i, j + 1])): 
                                return False
                            i = j
                            break
            elif tkn in section_ender:
                if len(stack) == 0 or stack[-1] != tkn:
                    return False
                stack.pop()

            # boolean and number
            elif tkn == "true" or tkn == "false" or tkn == "null"  or is_number(tkn):
                if len(statement) != 0:
                    return False
                statement.append(tkn)
            else:
                return False
        i += 1
    # check for rouge commas
    if len(statement) == 0 and is_comma:
        return False
    return True

print(is_valid_json("tests/step4/valid2.json"))
