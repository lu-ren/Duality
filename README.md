# Summary
Amnesiac is a file-based secret password generator. To elaborate, Amnesiac generates a password for a site by taking in a file containing a secret, a pin number, and a domain name. It uses these to generate a strong password using SHA512.

# Usage

To generate a secret, use the `-s` option.
Example: python3 amnesiac.py -s 100 | tee secret.txt

Here, `-s` signifies that the secret is 100 bytes long.

Next, save secret.txt somewhere safe. You will need to use it to generate passwords.

To generate a password for google.com,
python3 amnesiac.py -i secret.txt -p 5001 -t google.com

Here `-i` is the filepath of the secret, `-p` is the pin, and `-t` is the domain.
