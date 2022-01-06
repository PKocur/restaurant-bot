from random import Random

nearby_keys = {
    'a': ['s'],
    'b': ['v', 'n'],
    'c': ['x', 'v'],
    'd': ['s', 'f'],
    'e': ['w', 'r'],
    'f': ['d', 'g'],
    'g': ['f', 'h'],
    'h': ['g', 'j'],
    'i': ['u', 'o'],
    'j': ['h' 'k'],
    'k': ['j', 'l'],
    'l': ['k'],
    'm': ['n'],
    'n': ['b', 'm'],
    'o': ['i', 'p'],
    'p': ['o'],
    'q': ['w'],
    'r': ['e', 't'],
    's': ['d', 'a'],
    't': ['r', 'y'],
    'u': ['y', 'i'],
    'v': ['c', 'b'],
    'w': ['q', 'e'],
    'x': ['z', 'c'],
    'y': ['t', 'u'],
    'z': ['x'],
    ' ': [' ']
}


def get_typo(letter: str):
    random = Random()
    typo_list = nearby_keys.get(letter)
    random_typo = random.choice(range(len(typo_list)))
    return typo_list[random_typo]


def generate(sentences: list) -> list:
    typo_sentences = []
    for sentence in sentences:
        words = sentence.split(" ")
        typo_words = []
        random = Random()
        for word in words:
            if len(word) <= 2:
                typo_words.append("".join(word))
                continue
            word = list(word)
            letter_to_change = random.choice(range(len(word)))
            word[letter_to_change] = get_typo(word[letter_to_change])
            typo_words.append("".join(word))
        typo_sentences.append(typo_words)
    return typo_sentences


# open-time
print(generate(["is the restaurant open on at",
                "i will be on at",
                "can i come to you on at"]))

# menu
print(generate(["can i have the menu",
                "what kind of meals do you offer",
                "show me the menu"]))

# order
print(generate(["can i order something",
                "i want to order",
                "i want to eat",
                "i want next meal",
                "i want next order"]))
