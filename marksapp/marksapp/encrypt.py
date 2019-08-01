import base64
import pickle
import gc

import argon2
from argon2 import PasswordHasher as Hash
from cryptography.fernet import Fernet, InvalidToken


class PasswordError(Exception):
    pass


class Encryptor:
    def __init__(self):
        self.hasher = Hash(hash_len=32, salt_len=32)
        self.path = None
        self.key = None
        self.pw = None

    def read(self, path, pw):
        pw = bytes(pw, encoding="utf-8")
        with open(path) as file:
            encrypted_data = file.read()
        try:
            pickled_data = self.decrypt(encrypted_data, pw)
            data = pickle.loads(pickled_data)
            self.store_pw(pw)
            self.path = path
        except InvalidToken:
            raise PasswordError("Incorrect Password") from None
        return data

    def save(self, data, pw, path):
        self.path = path
        hash = self.hasher.hash(pw)
        key = self.format_b64s(self.get_key(hash))
        self.encrypt(data, hash, key)
        self.store_pw(bytes(pw, encoding="utf-8"))

    def resave(self, data):
        pw = self.get_pw()
        hash = self.hasher.hash(pw)
        key = self.format_b64s(self.get_key(hash))
        self.encrypt(data, hash, key)

    def store_pw(self, pw):
        self.key = Fernet.generate_key()
        f = Fernet(self.key)
        self.pw = f.encrypt(pw)
        del pw
        gc.collect()

    def get_pw(self):
        f = Fernet(self.key)
        pw = f.decrypt(self.pw).decode("utf-8")
        return pw

    def encrypt(self, data, hash, key):
        pickled_data = pickle.dumps(data)
        encrypted_data = Fernet(key).encrypt(pickled_data)
        header = self.create_header(hash)
        with open(self.path, "wb") as file:
            file.write(header + encrypted_data)

    def format_b64s(self, string):
        if len(string) % 4 != 0:
            while len(string) % 4 != 0:
                string = string + "="
        return bytes(string, "utf-8")

    def create_header(self, hash):
        elements = hash.split("$")[:-1]
        return bytes("$".join(elements) + "$", encoding="utf-8")

    def get_key(self, hash):
        return hash.split("$")[-1]

    def parse_file(self, file):
        elements = file.split("$")
        type = elements[1]
        if type == "argon2d":
            index = 0
        if type == "argon2d":
            index = 1
        if type == "argon2id":
            index = 2
        type = argon2.low_level.Type(index)
        version = self.create_dict(elements[2])["v"]
        settings = self.create_dict(elements[3])
        salt = base64.decodestring(self.format_b64s(elements[4]))
        digest = bytes(elements[5], encoding="utf-8")
        params = {
            "type": type,
            "version": version,
            "salt": salt,
            "time_cost": settings["t"],
            "memory_cost": settings["m"],
            "parallelism": settings["p"],
            "hash_len": 32,
        }
        return (digest, params)

    def create_dict(self, string):
        params = {}
        if "," in string:
            pairs = string.split(",")
        else:
            pairs = [string]
        for pair in pairs:
            key, value = pair.split("=")
            params[key] = int(value)
        return params

    def decrypt(self, encrypted_data, pw):
        digest, params = self.parse_file(encrypted_data)
        hash = argon2.low_level.hash_secret(pw, **params).decode("utf-8")
        key = self.format_b64s(self.get_key(hash))
        data = Fernet(key).decrypt(digest)
        return data


if __name__ == "__main__":
    e = Encryptor()
    d = {"Alex": 36, "Karo": 30, "Oksar": 1}
    e.save(d, "Goose", "me.txt")
    d["Noob"] = 7
    e.resave(d)
    try:
        nd = e.read("me.txt", "Goose")
        print(nd)
    except PasswordError as e:
        print(e)
