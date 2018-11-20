import hashlib
import time

def getVersionSentinel():

    gmtime = time.strftime("%a, %b %d %Y %H:%M:%S +0000", time.gmtime())

    md5 = hashlib.md5(bytes(gmtime, encoding='utf-8'))
    hexdigest = md5.hexdigest().upper()

    return gmtime, hexdigest

if __name__ == '__main__':

    print('{}\n{}'.format(*getVersionSentinel()))