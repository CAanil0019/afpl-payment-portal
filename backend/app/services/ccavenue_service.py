from Crypto.Cipher import AES
import hashlib
from urllib.parse import quote_plus

BLOCK_SIZE = 16


def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + chr(length) * length


def unpad(data):
    return data[:-ord(data[-1:])]


def encrypt(plainText, workingKey):
    iv = bytes.fromhex('000102030405060708090a0b0c0d0e0f')

    key = hashlib.md5(workingKey.encode()).digest()

    plainText = pad(plainText)

    cipher = AES.new(key, AES.MODE_CBC, iv)

    encryptedText = cipher.encrypt(
        plainText.encode()
    ).hex()

    return encryptedText


def decrypt(cipherText, workingKey):
    iv = bytes.fromhex('000102030405060708090a0b0c0d0e0f')

    key = hashlib.md5(workingKey.encode()).digest()

    cipher = AES.new(key, AES.MODE_CBC, iv)

    decryptedText = cipher.decrypt(
        bytes.fromhex(cipherText)
    ).decode()

    return unpad(decryptedText)