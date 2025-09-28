import string

import sympy
from sympy import Eq

from bestsupport_units_tests.units_lib import UnitBase, kg, s, K, A, mol, m, DIMENSIONLESS
from units_list import *


def find_formula(to_find: dict[str, UnitBase], known: UnitBase, known_symb: str):
    to_find_coefs = dict(zip(to_find.keys(), string.ascii_lowercase))
    to_find_coefs_rev = {val: key for key, val in to_find_coefs.items()}

    equations = []

    for meas_id, meas in enumerate(UNITS_INDEXES):
        known_meas = known.cur_dim[meas_id]

        to_find_values = [
            f"{val}*{coef}" for val_symb, coef in to_find_coefs.items()
            if (val := to_find[val_symb].cur_dim[meas_id]) != 0
        ]

        if not to_find_values:
            continue

        lhs = sympy.parse_expr(str(known_meas))
        rhs = sympy.parse_expr(' + '.join(to_find_values))

        equations.append(Eq(lhs, rhs))

    solved = sympy.solve(equations)

    result = []

    if not solved:
        print("\n\n\nРешений не найдено\n\n\n")
        return

    for coef, val in solved.items():
        meas_name = to_find_coefs_rev[str(coef)]
        print(f"{meas_name} = {val}")

        if val == 0:
            print(f"'{meas_name}' не участвует в процессе")
        else:
            result.append(f"{meas_name}**({val})")

    print("\nОбщий вид формулы:")

    res_lhs = known_symb
    res_rhs = f"k * {' * '.join(result)}"
    result_formula = f"{res_lhs} = {res_rhs}"

    print(result_formula)
    print("\nгде k - безразмерный коэффициент")

    return result_formula


if __name__ == "__main__":
    formulas = []

    print("Второй закон Ньютона:")
    formulas.append(find_formula({
        "m": kg,
        "a": m / s ** 2,
    }, m * kg / s ** 2, "F"))

    print("Закон всемирного тяготения Ньютона:")
    formulas.append(find_formula({
        "m": kg,
        "G": m ** 3 / (kg * s ** 2),
        "r": m,
    }, m * kg / s ** 2, "F"))

    print("Закон Ома:")
    formulas.append(find_formula({
        "I": A,
        "R": kg * m ** 2 / (s ** 3 * A ** 2),
    }, kg * m ** 2 / (s ** 3 * A), "U"))

    print("Уравнение состояния идеального газа (Уравнение Клапейрона-Менделеева):")
    formulas.append(find_formula({
        "V": m ** 3,
        "v": mol,
        "R": kg * m ** 2 / (s ** 2 * K * mol),
        "T": K,
    }, kg / (m * s ** 2), "P"))

    print("Закон Стефана — Больцмана для излучения абсолютно чёрного тела:")
    formulas.append(find_formula({
        "σ": kg * s ** -3 * K ** -4,
        "A": m ** 2,
        "T": K,
    }, kg * m ** 2 / s ** 3, "P"))

    print("Сила сопротивления воздуха (лобового сопротивления):")
    formulas.append(find_formula({
        "C": DIMENSIONLESS,
        "p": kg / m ** 3,
        "S": m ** 2,
        "v": m / s,
    }, m * kg / s ** 2, "F"))

    print("Вектор Умова-Пойнтинга для электромагнитной волны:")
    formulas.append(find_formula({
        "E": (kg * m) / (s ** 3 * A),
        "H": A / m,
    }, kg / s ** 3, "S"))

    print("Давление излучения абсолютно чёрного тела:")
    formulas.append(find_formula({
        "h": kg * m ** 2 / s,
        "c": m / s,
        "k_B": kg * m ** 2 / (s ** 2 * K),
        "T": K,
    }, kg / (m * s ** 2), "P_rad"))

    print("Мощность излучения диполя Герца:")
    formulas.append(find_formula({
        "μ0": kg * m / (s ** 2 * A ** 2),
        "ω": 1 / s,
        "p0": A * s * m,
        "c": m / s,
    }, kg * m ** 2 / s ** 3, "P"))

    print("\n\n")
    for formula in formulas:
        print(formula)
