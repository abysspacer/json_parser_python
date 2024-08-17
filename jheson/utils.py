from os import path

def read_from_file(file_path):
    with open(file_path, "r") as fh:
        return fh.read()

def get_ready_to_parse_data(data):
    return read_from_file(data) if path.isfile(data) else data
