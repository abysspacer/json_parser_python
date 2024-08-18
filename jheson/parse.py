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

def string_to_number(string):
    try:
        return int(string)
    except Exception:
        pass
    
    try:
        return float(string)
    except Exception:
        pass

def is_valid_json(data):
    """
    validates json data and return true or false accordngly
    """
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

def parse_json(data):

    def throw_error(tkn):
        raise ValueError(f"Unexpected token: {tkn}")
    
    section_starter = ["{", "["]
    section_ender = ["}", "]"]
    tokens = tokenize_data(data) 
    # basic invalid cases
    if len(tokens) == 0 or (tokens[0] not in section_starter) or (tokens[-1] not in section_ender) or section_ender.index(tokens[-1]) != section_starter.index(tokens[0]):
        raise ValueError("Invalid data format")

    # lexical characteristic
    # 1 => object
    # 2 => array
    lex_char = 1 if tokens[0] == "{" else 2
    dic = {}
    arr = []
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
                throw_error(tkn)
            elif tkn[0] == "\"":
                if tkn[-1] != "\"":
                    throw_error(tkn)
                if len(statement) == 0:
                    is_comma = False
                    statement.append(tkn[1:-1])
                elif statement[-1] == ":":
                    statement.append(tkn[1:-1])
                else:
                    throw_error(tkn)

            # seperator detection
            elif tkn == ":":
                if len(statement) != 1:
                    throw_error(tkn)
                statement.append(tkn)
            elif tkn == ",":
                if len(statement) != 3:
                    throw_error(tkn)
                if is_number(statement[-1]):
                    dic[statement[0]] = string_to_number(statement[-1])
                elif statement[-1] == "true":
                    dic[statement[0]] = string_to_number(True)
                elif statement[-1] == "false":
                    dic[statement[0]] = string_to_number(False)
                elif statement[-1] == "null":
                    dic[statement[0]] = string_to_number(None)
                else:    
                    dic[statement[0]] = statement[-1]
                statement = []
                is_comma = True

            # section detection
            elif tkn in section_starter:
                if not len(statement) or statement[-1] != ":":
                    throw_error(tkn)
                layer_stack_height = len(stack)
                for j in range(i, len(tokens)):
                    if tokens[j] in section_starter:
                        stack.append(section_ender[section_starter.index(tokens[j])])
                    elif tokens[j] in section_ender:
                        if len(stack) == 0 or stack[-1] != tokens[j]:
                            throw_error(tokens[j])
                        stack.pop()
                        if len(stack) == layer_stack_height:
                            inner = parse_json(" ".join(tokens[i: j + 1]))
                            statement.append(inner)
                            i = j
                            break
            elif tkn in section_ender:
                if len(stack) == 0 or stack[-1] != tkn:
                    throw_error(tkn)
                stack.pop()
            
            # boolean and number
            elif tkn == "true" or tkn == "false" or tkn == "null"  or is_number(tkn):
                if len(statement) != 2:
                    throw_error(tkn)
                statement.append(tkn)
            else:
                throw_error(tkn)
        
        # in array
        else:
            # string detection
            if tkn[0] == "'":
                throw_error(tkn)
            elif tkn[0] == "\"":
                if tkn[-1] != "\"":
                    throw_error(tkn[1:-1])
                if len(statement) == 0:
                    is_comma = False
                    statement.append(tkn[1:-1])
                else:
                    throw_error(tkn)

            # seperator detection
            elif tkn == ":":
                throw_error(tkn)
            elif tkn == ",":
                if len(statement) != 1:
                    throw_error(tkn)
                if is_number(statement[0]):
                    arr.append(string_to_number(statement[0]))
                elif statement[0] == "true":
                    arr.append(True)
                elif statement[0] == "false":
                    arr.append(False)
                elif statement[0] == "null":
                    arr.append(None)
                else:
                    arr.append(statement[0])
                statement = []
                is_comma = True

            # section detection
            elif tkn in section_starter:
                layer_stack_height = len(stack)
                for j in range(i, len(tokens)):
                    if tokens[j] in section_starter:
                        stack.append(section_ender[section_starter.index(tokens[j])])
                    elif tokens[j] in section_ender:
                        if len(stack) == 0 or stack[-1] != tokens[j]:
                            throw_error(tkn)
                        stack.pop()
                        if len(stack) == layer_stack_height:
                            inner = is_valid_json(" ".join(tokens[i: j + 1]))
                            statement.append(inner)
                            i = j
                            break
            elif tkn in section_ender:
                if len(stack) == 0 or stack[-1] != tkn:
                    throw_error(tkn)
                stack.pop()

            # boolean and number
            elif tkn == "true" or tkn == "false" or tkn == "null"  or is_number(tkn):
                if len(statement) != 0:
                    throw_error(tkn)
                statement.append(tkn)
            else:
                throw_error(tkn)
        i += 1

    # check for rouge commas
    if len(statement) == 0 and is_comma:
        throw_error(",")
    elif len(statement):
        #TODO: add number eval here
        #TODO: add null and bool eval
        if lex_char == 2:
            if is_number(statement[0]):
                arr.append(string_to_number(statement[0]))
            elif statement[0] == "true":
                arr.append(True)
            elif statement[0] == "false":
                arr.append(False)
            elif statement[0] == "null":
                arr.append(None)
            else:
                arr.append(statement[0])
        else:
            try:
                if is_number(statement[-1]):
                    dic[statement[0]] = string_to_number(statement[-1])
                elif statement[-1] == "true":
                    dic[statement[0]] = string_to_number(True)
                elif statement[-1] == "false":
                    dic[statement[0]] = string_to_number(False)
                elif statement[-1] == "null":
                    dic[statement[0]] = string_to_number(None)
                else:    
                    dic[statement[0]] = statement[-1]
            except Exception:
                raise ValueError("Invalid JSON syntax")

    if len(arr) == 0:
        return dic
    else:
        return arr


tests = [
    "tests/step1/valid.json",
    "tests/step1/invalid.json",
    "tests/step2/valid.json",
    "tests/step2/valid2.json",
    "tests/step2/invalid.json",
    "tests/step2/invalid2.json",
    "tests/step3/valid.json",
    "tests/step3/invalid.json",
    "tests/step4/valid.json",
    "tests/step4/valid2.json",
    "tests/step4/invalid.json",
    "{\"names\": [\"Ruka\", \"Xero\", \"Hasan\"]}",
    "[12, 13, 14, true, \"hi\"]"
        ]

for test in tests:
    print(test)
    try:
        print(parse_json(test))
    except ValueError as err:
        print(err.args[0])
