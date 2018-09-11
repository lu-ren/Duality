import argparse
import base64
import hashlib
import getpass
import math
import os
import string
import sys
import pyperclip

from git import Repo

CACHE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.cache/')

def createFileSecret(nbytes):

    return base64.b64encode(os.urandom(nbytes))

def getGeneratedSecret(filePath, pin):

    with open(filePath, 'r') as f:
        fileSecret = f.read().strip()

    t = fileSecret + pin
    m = hashlib.sha512()
    m.update(t.encode('utf-8'))

    return m.digest()

def getGeneratedPasswordBytes(seed, target):

    seed += target.encode('utf-8')
    m = hashlib.sha512()
    m.update(seed)
    d = m.digest()

    return d

def transformAndSimplify(passwdBytes):

    lowercases = list(string.ascii_lowercase)
    capitals = list(string.ascii_uppercase)
    numbers = list(string.digits)
    specials = list('!@#$%&')
    chunkLength = math.floor(len(passwdBytes)/10)

    values = []

    for chunk in chunkBytes(passwdBytes, chunkLength):
        values.append(int.from_bytes(chunk, byteorder='big', signed=False))

    specialCharacter = specials[values[0] % len(specials)]
    numberCharacter = numbers[values[1] % len(numbers)]
    capitalCaseCharacters = [capitals[values[i] % len(capitals)] for i in range(2, 6)]
    lowerCaseCharacters = [lowercases[values[i] % len(lowercases)] for i in range(6, len(values))]

    passwd = ''.join(capitalCaseCharacters) + ''.join(lowerCaseCharacters) + numberCharacter + specialCharacter

    return passwd

def chunkBytes(string, length):

    return (string[0 + i: length + i] for i in range(0, len(string), length))

if __name__ == '__main__':
    
    def pullRepoCache(repoUrl):
        os.mkdir(CACHE_DIR)
        repo = Repo.init(CACHE_DIR)
        origin = repo.create_remote('origin', repoUrl)
        origin.fetch()
        origin.pull(origin.refs[0].remote_head)
    
    def getFilePartPath():
        for path in os.listdir(CACHE_DIR):
            if '.git' not in path:
                return os.path.join(CACHE_DIR, path)

    parser = argparse.ArgumentParser(description='A secret file based password generator')
    parser.add_argument('-t', action='store', dest='target',
            help='Target domain')
    parser.add_argument('-s', action='store', dest='secret',
            help='Create a secret output with n number of bytes')

    parsed = parser.parse_args()

    if not (parsed.secret or parsed.target):
        parser.print_help()
        sys.exit(1)

    if parsed.target and parsed.secret:
            parser.print_help()
            sys.exit(1)

    if parsed.secret:
        print(createFileSecret(int(parsed.secret)))
        sys.exit(0)

    if not os.path.isdir(CACHE_DIR):
        repoUrl = input('Please enter the git repo url containing the file secret: ').strip()
        pullRepoCache(repoUrl)

    pin = getpass.getpass(prompt='Enter pin: ')
    seed = getGeneratedSecret(getFilePartPath(), pin)
    passwdBytes = getGeneratedPasswordBytes(seed, parsed.target)

    passwdString = transformAndSimplify(passwdBytes)
    pyperclip.copy(passwdString)
    print('Password is copied to system clipboard!')
