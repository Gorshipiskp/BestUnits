from __future__ import annotations

from decimal import Decimal
from typing import Union, Any, TypeAlias, Optional

from numpy import ndarray, array_equal
from numpy import zeros

from bestsupport_units_tests.config import SORT_MEASURES_BY_DIM_POWER, POWER_SIGN, DIMENSIONLESS_STR, MULTIPLY_SIGN
from bestsupport_units_tests.units_list import *

NUMERIC_TYPE: TypeAlias = (int, float, Decimal)
NUMERIC_UNION: TypeAlias = Union[int, float, Decimal]


def make_zero_dim() -> ndarray:
    return zeros(LEN_DIM)


class UnitBase:
    cur_dim: ndarray

    def __init__(self, init_dim: Optional[ndarray] = None) -> None:
        if init_dim is None:
            self.cur_dim: ndarray = make_zero_dim()
        else:
            if init_dim.shape != (LEN_DIM,):
                raise ValueError("Init dim doesn't shape")
            self.cur_dim: ndarray = init_dim

        self.cur_dim.setflags(write=False)

    def is_dimensionless(self) -> bool:
        return not self.cur_dim.any()

    @staticmethod
    def __check_is_unit__(arg: Any):
        if isinstance(arg, UnitBase):
            return True
        raise TypeError(f"Argument is not UnitBase type (current type: {type(arg)})")

    def __hash__(self) -> int:
        return hash(self.cur_dim.tobytes())

    def __repr__(self) -> str:
        return f"UnitBase({self.__str__()})"

    def __str__(self) -> str:
        # todo: Добавить в конфиг возможность форматировать степени в виде ² (надстрочные символы)
        str_dims = []

        enumerated_dim = enumerate(self.cur_dim)
        if SORT_MEASURES_BY_DIM_POWER:
            to_for = sorted(enumerated_dim, key=lambda dim_info: dim_info[1], reverse=True)
        else:
            to_for = enumerated_dim

        for dim_id, dim in to_for:
            if dim == 0:
                continue

            if dim < 0:
                dim_str = f"{POWER_SIGN}({dim})"
            elif dim == 1:
                dim_str = ""
            else:
                dim_str = f"{POWER_SIGN}{dim}"

            str_dims.append(f"{UNITS_INDEXES[dim_id]}{dim_str}")

        if not str_dims:
            return DIMENSIONLESS_STR

        return MULTIPLY_SIGN.join(str_dims)

    def __add__(self, other: UnitBase) -> UnitBase:
        self.__check_is_unit__(other)

        if self == other:
            return UnitBase(self.cur_dim)
        raise ValueError("Addition is impossible with mismatched Units")

    def __radd__(self, other: NUMERIC_UNION) -> UnitBase:
        if not isinstance(other, NUMERIC_TYPE):
            raise TypeError(f"Summand must be numeric in __radd__, got {type(other)}")

        if not self.is_dimensionless():
            raise ValueError(
                "Addition is impossible with mismatched Units (__radd__, adding with number, but self is not dimensionless)")
        return UnitBase(self.cur_dim)

    def __sub__(self, other: UnitBase) -> UnitBase:
        self.__check_is_unit__(other)

        if self == other:
            return UnitBase(self.cur_dim)
        raise ValueError("Subtraction is impossible with mismatched Units")

    def __rsub__(self, other: NUMERIC_UNION) -> UnitBase:
        if not isinstance(other, NUMERIC_TYPE):
            raise TypeError(f"Minuend must be numeric in __rsub__, got {type(other)}")

        if not self.is_dimensionless():
            raise ValueError(
                "Subtraction is impossible with mismatched Units (__rsub__, subtraction with number, but self is not dimensionless)")
        return UnitBase(self.cur_dim)

    def __mul__(self, other: UnitBase) -> UnitBase:
        self.__check_is_unit__(other)

        return UnitBase(self.cur_dim + other.cur_dim)

    def __rmul__(self, other: NUMERIC_UNION) -> UnitBase:
        if not isinstance(other, NUMERIC_TYPE):
            raise TypeError(f"Multiplier must be numeric in __rmul__, got {type(other)}")

        return UnitBase(self.cur_dim)

    def __truediv__(self, other: UnitBase) -> UnitBase:
        self.__check_is_unit__(other)

        return UnitBase(self.cur_dim - other.cur_dim)

    def __rtruediv__(self, other: NUMERIC_UNION) -> UnitBase:
        if not isinstance(other, NUMERIC_TYPE):
            raise TypeError(f"Multiplier must be numeric in __rtruediv__, got {type(other)}")

        return UnitBase(-self.cur_dim)

    def __pow__(self, power: NUMERIC_UNION) -> UnitBase:
        if not isinstance(power, NUMERIC_TYPE):
            raise TypeError(f"Power must be numeric, got {type(power)}")

        return UnitBase(self.cur_dim * power)

    def __rpow__(self, base: UnitBase):
        if self.is_dimensionless():
            return UnitBase(DIMENSIONLESS)

        raise TypeError(f"Power cannot be dimensioned Unit")

    def __neg__(self) -> UnitBase:
        return UnitBase(-self.cur_dim)

    def __eq__(self, other: UnitBase) -> bool:
        self.__check_is_unit__(other)

        return array_equal(self.cur_dim, other.cur_dim)

    def __ne__(self, other: UnitBase) -> bool:
        return not self == other


def unit_dim(unit: str, raise_error: bool):
    if unit in BASE_UNITS:
        return BASE_UNITS[unit]
    if unit in COMPOSITE_UNITS:
        return COMPOSITE_UNITS[unit]
    if unit in SPECIAL_UNITS:
        return SPECIAL_UNITS[unit][0]

    if raise_error:
        raise ValueError(f"Неизвестная единица: {unit}")
    return False


DIMENSIONLESS = UnitBase()

m = UnitBase(BASE_UNITS["м"])
kg = UnitBase(BASE_UNITS["кг"])
s = UnitBase(BASE_UNITS["с"])
A = UnitBase(BASE_UNITS["А"])
K = UnitBase(BASE_UNITS["К"])
mol = UnitBase(BASE_UNITS["моль"])
kd = UnitBase(BASE_UNITS["кд"])
rad = UnitBase(BASE_UNITS["рад"])
bit = UnitBase(BASE_UNITS["бит"])
