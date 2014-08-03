import base64


KEY = "THIS_IS_MY_CRAZY_SILLY_FRESH_KEY_)(!%#($)@^%@&$^#("


def encode(string):
    encoded_chars = []
    for i in xrange(len(string)):
        key_c = KEY[i % len(KEY)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return base64.urlsafe_b64encode(encoded_string)


def decode(string):
    decoded_chars = []
    string = base64.urlsafe_b64decode(string)
    for i in xrange(len(string)):
        key_c = KEY[i % len(KEY)]
        encoded_c = chr(abs(ord(string[i]) - ord(key_c) % 256))
        decoded_chars.append(encoded_c)
    decoded_string = "".join(decoded_chars)
    return decoded_string
