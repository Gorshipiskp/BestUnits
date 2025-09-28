# todo: Это файл, где будет обработка (парсинг) ручного ввода и перевода его в вектор единиц измерения (например, Н*кг -> [1, 0, ...])

def clean_unit_str(unit_str: str) -> str:
    return unit_str.replace(" ", "").lower()


def tokenize_unit_str(unit_str: str) -> list[str]:
    tokens: list[str] = []

    ind = 0
    while ind < len(unit_str):
        char = unit_str[ind]

        print(char)

        ind += 1

    return tokens


def parse_unit_str(unit_str: str) -> ...:
    cleaned_str = clean_unit_str(unit_str)
    tokens: list[str] = tokenize_unit_str(cleaned_str)

    pass


parse_unit_str("Н/кг*Па")
