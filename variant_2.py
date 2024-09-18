import os
import random
import string
from Crypto.Cipher import AES
import hashlib
import json


def prepare(filename: str, n: int) -> str:
    dictionary = []
    expanded_data = []

    for byte in range(0, 256):
        current_chunk = [byte, ] + [0] * (n - 1)
        dictionary.append(current_chunk)

    with open(filename, "rb") as file:
        data = file.read()
    for byte in data:
        current_chunk = [byte, ] + [0] * (n - 1)
        expanded_data.append(current_chunk)

    split = os.path.splitext(filename)
    expanded_filename = split[0] + "_expanded" + split[1]

    with open(expanded_filename, "wb") as file:
        for chunk in dictionary:
            file.write(bytes(chunk))
        for chunk in expanded_data:
            file.write(bytes(chunk))

    return expanded_filename


def split_into_chunks(input_list, chunk_size):
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def encode(filename: str, hash_input_data: str) -> str:
    key = hashlib.sha256(hash_input_data.encode()).digest()

    with open(filename, "rb") as file_in:
        data = file_in.read()
    encoded_data = []
    cipher = AES.new(key, AES.MODE_ECB)
    data_in_chunks = split_into_chunks(data, 16)
    for chunk in data_in_chunks:
        encoded_data.append(cipher.encrypt(bytes(chunk)))

    split = os.path.splitext(filename)
    encoded_filename = split[0] + "_encoded" + split[1]

    with open(encoded_filename, "wb") as file_out:
        for chunk in encoded_data:
            file_out.write(chunk)

    return encoded_filename


def translate(encoded_filename: str):
    with open(encoded_filename, "rb") as file_in:
        data = file_in.read()
    dictionary_part = [byte for byte in data[:(256 * 16)]]
    match_table = []
    chunks = split_into_chunks(dictionary_part, 16)
    for byte in range(0, 256):
        match_table.append((chunks[byte], byte))
    with open('match_table.json', 'w') as file_out:
        json.dump(match_table, file_out)


def decode(filename: str):
    output = []
    with open('match_table.json', 'r') as match_table_file:
        match_table = {tuple(key): value for key, value in json.load(match_table_file)}
    with open(filename, 'rb') as file:
        data = file.read()
    data = [byte for byte in data[4096:]]
    data_in_chunks = split_into_chunks(data, 16)
    for chunk in data_in_chunks:
        output.append(match_table[tuple(chunk)])

    split = os.path.splitext(filename)
    decoded_filename = split[0] + "_decoded" + split[1]

    with open(decoded_filename, "wb") as file:
        for byte in output:
            in_hex = hex(byte)[2:]
            if len(in_hex) % 2 == 0:
                file.write(bytes.fromhex(in_hex))
            else:
                in_hex = '0' + in_hex
                file.write(bytes.fromhex(in_hex))


def generate_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def main():
    expanded_filename = prepare("jackal.jpg", 16)
    encoded_filename = encode(expanded_filename, generate_random_string(8))
    translate(encoded_filename)
    decode(encoded_filename)


main()
