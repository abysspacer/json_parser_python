from utils import get_ready_to_parse_data

def tokenize_data(data):

    ready_to_tokenize = get_ready_to_parse_data(data)
    if len(ready_to_tokenize) == 0:
        return []
    tokens = []
    i = 0
    seperators = ["{", "}", "[", "]", ",", ":"]
    while i < len(ready_to_tokenize):
        # check for strings
        if ready_to_tokenize[i] == "\"":
            start_index = i
            i += 1
            while ready_to_tokenize[i] != "\"" and i + 1 < len(ready_to_tokenize):
                i += 1
            if i + 1 >= len(ready_to_tokenize):
                tokens.append(ready_to_tokenize[start_index:])
            else:
                tokens.append(ready_to_tokenize[start_index: i + 1])
        
        # seperator check
        elif ready_to_tokenize[i] in seperators:
            tokens.append(ready_to_tokenize[i])
        # basic check
        elif not ready_to_tokenize[i].isspace() and not (ready_to_tokenize[i] in seperators):
            start_index = i
            i += 1
            while not ready_to_tokenize[i].isspace() and not (ready_to_tokenize[i] in seperators) and i + 1 < len(ready_to_tokenize):
                i += 1
            tokens.append(ready_to_tokenize[start_index : i])
            continue
        i += 1
    return tokens

def is_number(data):
    try:
        float(data)
    except Exception:
        return False
    return True

def is_valid_json(tokens):
    section_starter = ["{", "["]
    section_ender = ["}", "]"]
    
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

