"""
Description:
  Outputs the base64 decoded contents of the clipboard to standard out.

Usage:
  1. Copy base64 encoded data to your clipboard.
  2. Run: python base64_decode.py
"""

import base64
import binascii
import json

import pyperclip


def main():
    encoded_data = pyperclip.paste()

    decoded_data = ''
    try:
        decoded_data = base64.decodestring(encoded_data)
    except binascii.Error:
        print "Error: Clipboard contents is not base64 encoded.\n"
        print "Usage: Copy base64 encoded data to your clipboard."
        exit(1)

    json_obj = json.loads(decoded_data)
    print json.dumps(json_obj, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
