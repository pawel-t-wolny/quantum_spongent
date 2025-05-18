import random
import string

NUM_WORDS = 1000
MIN_LEN = 1
MAX_LEN = 32
CHARS = string.ascii_letters + string.digits  # a-zA-Z0-9

def generate_word(length):
    return ''.join(random.choices(CHARS, k=length))

def main():
    for _ in range(NUM_WORDS):
        word_len = random.randint(MIN_LEN, MAX_LEN)
        print(generate_word(word_len))

if __name__ == "__main__":
    main()
