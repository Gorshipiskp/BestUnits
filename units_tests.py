import unittest

from units_list import (
    COMPOSITE_UNITS,
    LEN_DIM,
    BASE_UNITS,
    SPECIAL_UNITS,
    PREFIXES_RU
)

IGNORED_UNITS_VARIATIONS_CONFLICTS = [
    "Гц",  # Гигацентнер и Герц
    "Тл",  # Тералитр и Тесла
]


# todo: Переведите все-все доки на английский, месье
# todo: Добавить тестов на все херни

class TestUnits(unittest.TestCase):
    def test_unit_dimensions(self):
        """Проверка длины размерности всех единиц"""
        units_to_check = {**COMPOSITE_UNITS}

        for unit_name, dim in BASE_UNITS.items():
            units_to_check[unit_name] = dim

        for unit_name, (dim, _) in SPECIAL_UNITS.items():
            units_to_check[unit_name] = dim

        for unit, dim in units_to_check.items():
            with self.subTest(unit=unit):
                self.assertEqual(
                    len(dim),
                    LEN_DIM,
                    msg=f"{unit} имеет неверную длину размерности"
                )

    def test_prefix_conflicts(self):
        """Проверка конфликтов префиксов с существующими единицами"""
        existing_units = set(BASE_UNITS) | set(COMPOSITE_UNITS) | set(SPECIAL_UNITS)
        candidate_map = {}

        for p_name, p_info in PREFIXES_RU.items():
            symbols = p_info.get("symbols", [])
            if not symbols:
                continue
            for sym in symbols:
                for unit in existing_units:
                    candidate = f"{sym}{unit}"
                    candidate_map.setdefault(candidate, []).append((p_name, sym, unit))

        for candidate, entries in candidate_map.items():
            if candidate in IGNORED_UNITS_VARIATIONS_CONFLICTS:
                continue
            self.assertNotIn(
                candidate,
                existing_units,
                msg=f"{candidate} конфликтует с существующей единицей"
            )

        for candidate, entries in candidate_map.items():
            if len(entries) > 1 and candidate not in IGNORED_UNITS_VARIATIONS_CONFLICTS:
                self.fail(
                    f"Конфликт префиксов для {candidate}: {entries}"
                )


if __name__ == "__main__":
    unittest.main()
