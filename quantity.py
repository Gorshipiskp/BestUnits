from __future__ import annotations

import decimal
from decimal import Decimal
from typing import Union, Literal, TypeAlias, get_args, Final, Optional

from numpy import ndarray

from bestsupport_units_tests.config import DECIMAL_PRECISE, DEFAULT_ERROR_CALCULATION_TYPE
from bestsupport_units_tests.units_lib import UnitBase, NUMERIC_UNION, NUMERIC_TYPE, kg, m, DIMENSIONLESS

MATH_VALUE_UNION: TypeAlias = Union["Quantity", NUMERIC_UNION]

MAX_DEVIATION: Final[str] = "MAX_DEVIATION"
AVG_SQRT_DEVIATION: Final[str] = "AVG_SQRT_DEVIATION"

ERROR_CALCULATION_TYPES: TypeAlias = Literal["MAX_DEVIATION", "AVG_SQRT_DEVIATION"]

decimal.getcontext().prec = DECIMAL_PRECISE


# todo: Сделать методы .to(unit) и .normalize() для перевода в СИ
# todo: Сделать метод для перевода в составные единицы (из фундаментальных в, например, 'Н') .to_base()
# todo: Добавить константы (G = Quantity(6.674e-11, m**3 / (kg*s**2)))
# todo: Парсер (parse("9.81 м/с²") → Quantity(9.81, m/s**2))
# todo: Перевод в наиболее подходящие единицы .best_unit() (Quantity(3600, "с").best_unit()  # "1 ч"; Quantity(1500, "м").best_unit()  # "1.5 км")
# todo: Добавить LaTeX-вид
# todo: Добавить возможность добавлять свои единицы измерения, переводы (масштабируемость, а ещё приколы по типу “мана”, “энергия выстрела из railgun”)


class Quantity:
    value: Decimal
    measure: UnitBase
    error: Decimal

    def __init__(self, init_value: Union[NUMERIC_UNION, str], init_measure: Optional[UnitBase, ndarray] = None,
                 error: Optional[NUMERIC_UNION, str] = None,
                 error_calculation_type: ERROR_CALCULATION_TYPES = DEFAULT_ERROR_CALCULATION_TYPE) -> None:
        if isinstance(init_value, (int, float, str)):
            self.value: Decimal = Decimal(str(init_value))
        elif isinstance(init_value, Decimal):
            self.value: Decimal = init_value
        else:
            raise TypeError(f"Unknown type of init_value {type(init_value)}")

        if isinstance(init_measure, ndarray) or init_measure is None:
            self.measure: UnitBase = UnitBase(init_measure)
        elif isinstance(init_measure, UnitBase):
            self.measure: UnitBase = init_measure
        else:
            raise TypeError(f"Unknown type of init_measure {type(init_measure)}")

        if isinstance(error, (int, float, str)):
            self.error: Decimal = Decimal(str(error))
        elif isinstance(error, Decimal):
            self.error: Decimal = error
        elif error is None:
            self.error: Decimal = Decimal("0")
        else:
            raise TypeError(f"Unknown type of error (inaccuracy) {type(error)}")

        if error_calculation_type in get_args(ERROR_CALCULATION_TYPES):
            self.error_calc_type = error_calculation_type
        else:
            raise TypeError(f"Unknown error (inaccuracy) calculation type {error_calculation_type}")

    def __calc_error_addsub__(self, error1: Decimal, error2: Decimal) -> Decimal:
        if self.error_calc_type == MAX_DEVIATION:
            return error1 + error2
        elif self.error_calc_type == AVG_SQRT_DEVIATION:
            return (error1 ** 2 + error2 ** 2).sqrt()

        raise TypeError(f"Unknown error (inaccuracy) calculation type {self.error_calc_type}")

    def __calc_error_muldiv__(self, q1: Quantity, q2: Quantity, q3_new_value: Decimal) -> Decimal:
        if self.error_calc_type == MAX_DEVIATION:
            return q3_new_value * (q1.error / q1.value + q2.error / q2.value)
        elif self.error_calc_type == AVG_SQRT_DEVIATION:
            return q3_new_value * ((q1.error / q1.value) ** 2 + (q2.error / q2.value) ** 2).sqrt()

        raise TypeError(f"Unknown error (inaccuracy) calculation type {self.error_calc_type}")

    def __calc_error_pow_numeric_power__(self, q1_base: Quantity, q2_power: NUMERIC_UNION,
                                         q3_new_value: Decimal) -> Decimal:
        if self.error_calc_type == MAX_DEVIATION:
            return q3_new_value * (abs(q2_power) * q1.error / q1.value)
        elif self.error_calc_type == AVG_SQRT_DEVIATION:
            return q3_new_value * (abs(q2_power) * q1_base.error / q1_base.value)

        raise TypeError(f"Unknown error (inaccuracy) calculation type {self.error_calc_type}")

    def __calc_error_pow__(self, q1_base: Quantity, q2_power: Quantity, q3_new_value: Decimal) -> Decimal:
        if self.error_calc_type == MAX_DEVIATION or self.error_calc_type == AVG_SQRT_DEVIATION:
            under_sqrt = (q2_power.value * (q1_base.error / q1_base.value)) ** 2 + (
                    q1_base.value.ln() * q2_power.error) ** 2
            return q3_new_value * under_sqrt.sqrt()

        raise TypeError(f"Unknown error (inaccuracy) calculation type {self.error_calc_type}")

    def __calc_error_pow_numeric_base__(self, q1_base: Decimal, q2_power: Quantity, q3_new_value: Decimal) -> Decimal:
        if self.error_calc_type == MAX_DEVIATION or self.error_calc_type == AVG_SQRT_DEVIATION:
            return q1_base ** q2_power.value * q1_base.ln() * q2_power.error

        raise TypeError(f"Unknown error (inaccuracy) calculation type {self.error_calc_type}")

    def __new_quantity__(self, new_value: Decimal, new_measure: UnitBase, error: Optional[Decimal] = None) -> Quantity:
        if error is None:
            error = self.error
        return Quantity(new_value, new_measure, error=error, error_calculation_type=self.error_calc_type)

    def is_dimensionless(self) -> bool:
        return self.measure.is_dimensionless()

    def __str__(self) -> str:
        if self.measure.is_dimensionless():
            measure_str = ""
        else:
            measure_str = f" {self.measure}"

        if self.error == 0:
            error_str = f""
        else:
            error_str = f" ± {self.error}"

        return f"{self.value}{error_str}{measure_str}"

    def __repr__(self) -> str:
        if self.error == 0:
            return f"Quantity({self.value}, {repr(self.measure)})"
        return f"Quantity({self.value}±{self.error}, {repr(self.measure)})"

    def __hash__(self) -> int:
        return hash((self.value, self.measure))

    def __add__(self, other: MATH_VALUE_UNION) -> Quantity:
        if isinstance(other, NUMERIC_UNION):
            if self.is_dimensionless():
                return self.__new_quantity__(self.value + Decimal(str(other)), self.measure)
            raise TypeError(f"Quantity must be dimensionless in __add__ (with numeric operand), got {type(other)}")

        new_error = self.__calc_error_addsub__(self.error, other.error)
        return self.__new_quantity__(self.value + other.value, self.measure + other.measure, error=new_error)

    def __radd__(self, other: NUMERIC_UNION) -> Quantity:
        if not isinstance(other, NUMERIC_UNION):
            raise TypeError(f"Summand must be numeric in __radd__, got {type(other)}")

        if self.is_dimensionless():
            return self.__new_quantity__(self.value + Decimal(str(other)), self.measure)
        raise TypeError(f"Quantity must be dimensionless in __radd__ (with numeric operand), got {type(other)}")

    def __sub__(self, other: MATH_VALUE_UNION) -> Quantity:
        if isinstance(other, NUMERIC_UNION):
            if self.is_dimensionless():
                return self.__new_quantity__(self.value - Decimal(str(other)), self.measure)
            raise TypeError(f"Quantity must be dimensionless in __sub__ (with numeric operand), got {type(other)}")

        new_error = self.__calc_error_addsub__(self.error, other.error)
        return self.__new_quantity__(self.value - other.value, self.measure - other.measure, error=new_error)

    def __rsub__(self, other: NUMERIC_UNION) -> Quantity:
        if not isinstance(other, NUMERIC_UNION):
            raise TypeError(f"Summand must be numeric in __rsub__, got {type(other)}")

        if self.is_dimensionless():
            return self.__new_quantity__(Decimal(str(other)) - self.value, self.measure)
        raise TypeError(f"Quantity must be dimensionless in __rsub__ (with numeric operand), got {type(other)}")

    def __mul__(self, other: MATH_VALUE_UNION) -> Quantity:
        if isinstance(other, NUMERIC_UNION):
            return self.__new_quantity__(self.value * Decimal(str(other)), self.measure)

        new_value = self.value * other.value
        new_error = self.__calc_error_muldiv__(self, other, new_value)
        return self.__new_quantity__(new_value, self.measure * other.measure, error=new_error)

    def __rmul__(self, other: NUMERIC_UNION) -> Quantity:
        if isinstance(other, NUMERIC_TYPE):
            return self.__new_quantity__(self.value * other, self.measure)

        raise TypeError(f"Multiplier must be numeric in __rmul__, got {type(other)}")

    def __truediv__(self, other: MATH_VALUE_UNION) -> Quantity:
        if isinstance(other, NUMERIC_UNION):
            return self.__new_quantity__(self.value / Decimal(str(other)), self.measure)

        new_value = self.value / other.value
        new_error = self.__calc_error_muldiv__(self, other, new_value)
        return self.__new_quantity__(new_value, self.measure / other.measure, error=new_error)

    def __rtruediv__(self, other: NUMERIC_UNION) -> Quantity:
        if isinstance(other, NUMERIC_TYPE):
            return self.__new_quantity__(other / self.value, self.measure ** -1)

        raise TypeError(f"Multiplier must be numeric in __rtruediv__, got {type(other)}")

    def __pow__(self, power: MATH_VALUE_UNION) -> Quantity:
        if isinstance(power, NUMERIC_TYPE):
            new_value = self.value ** power
            new_error = self.__calc_error_pow_numeric_power__(self, power, new_value)
            return self.__new_quantity__(new_value, self.measure ** power, error=new_error)

        if power.is_dimensionless():
            new_value = self.value ** power.value
            new_error = self.__calc_error_pow__(self, power, new_value)
            return self.__new_quantity__(new_value, self.measure ** power.value, error=new_error)

        raise TypeError(f"Power must be numeric, got {type(power)}")

    def __rpow__(self, base: NUMERIC_UNION) -> Quantity:
        if isinstance(base, NUMERIC_TYPE):
            if not self.is_dimensionless():
                raise TypeError(f"Power must be dimensionless, but power is {repr(self.measure)}")

            new_value = base ** self.value
            new_error = self.__calc_error_pow_numeric_base__(base, self, new_value)

            return self.__new_quantity__(new_value, DIMENSIONLESS, error=new_error)
        raise TypeError(f"Multiplier must be numeric in __rtruediv__, got {type(base)}")


if __name__ == "__main__":
    q1 = Quantity(2, kg / m, error=0.1)
    q2 = Quantity(7, kg / m)

    print(q1 + q2)
