from utils import get_ready_to_parse_data

def tokenize_data(data):
    section_starter = ["{", "["]
    section_ender = ["}", "]"]

    def tokenize(string): 
        if string == "": return []
        tkn_lst = []
        # check for section delimiters
        for indicator in section_starter + section_ender:
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

def is_valid_json(data):
    section_starter = ["{", "["]
    section_ender = ["}", "]"]
    
    tokens = tokenize_data(data)
    
    # basic invalid cases
    if len(tokens) == 0 or (tokens[0] not in section_starter) or (tokens[-1] not in section_ender) or section_ender.index(tokens[-1]) != section_starter.index(tokens[0]): return False
    stack = []
    for tkn in tokens:

        # section detection
        if tkn in section_starter:
            stack.append(section_ender[section_starter.index(tkn)])
        elif tkn in section_ender:
            if len(stack) == 0 or stack[-1] != tkn:
                return False
            stack.pop()
    return True
