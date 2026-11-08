"""Verification suite covering scientific expressions, 16 unit categories & math solvers."""

from __future__ import annotations

import math

from calconv.evaluator import CalcError, evaluate, format_number
from calconv.solvers import (
    compute_bmi,
    compute_date_diff,
    compute_loan_and_compound,
    compute_statistics,
    solve_cubic,
    solve_linear_system,
    solve_quadratic,
)
from calconv.units import CATEGORIES, convert_all, convert_value


def _approx(a: float, b: float, tol: float = 1e-7) -> None:
    assert abs(a - b) <= tol * max(1.0, abs(b)), f"Expected {b}, got {a}"


def run_all_tests() -> None:
    # 1. Scientific Evaluator
    _approx(evaluate("2 + 3 * 4"), 14.0)
    _approx(evaluate("-3^2"), -9.0)
    _approx(evaluate("(-3)^2"), 9.0)
    _approx(evaluate("2^3^2"), 512.0)
    _approx(evaluate("2^-3"), 0.125)
    _approx(evaluate("5!"), 120.0)
    _approx(evaluate("2π"), 2.0 * math.pi)
    _approx(evaluate("2e"), 2.0 * math.e)
    _approx(evaluate("1.5e3"), 1500.0)
    _approx(evaluate("sin(30)", angle_mode="DEG"), 0.5)
    _approx(evaluate("cos(90)", angle_mode="DEG"), 0.0)
    _approx(evaluate("sin(180)", angle_mode="DEG"), 0.0)
    _approx(evaluate("tan(45)", angle_mode="DEG"), 1.0)
    _approx(evaluate("asin(0.5)", angle_mode="DEG"), 30.0)
    _approx(evaluate("sin(pi/2)", angle_mode="RAD"), 1.0)
    _approx(evaluate("sin(100)", angle_mode="GRAD"), 1.0)
    _approx(evaluate("10 nCr 3"), 120.0)
    _approx(evaluate("5 nPr 2"), 20.0)
    _approx(evaluate("√144 + ∛27"), 15.0)
    _approx(evaluate("3 yroot 27"), 3.0)
    _approx(evaluate("200 * 15%"), 30.0)
    _approx(evaluate("17 % 5"), 2.0)
    _approx(evaluate("gcd(48, 18)"), 6.0)
    _approx(evaluate("lcm(12, 18)"), 36.0)
    _approx(evaluate("sin(30 + cos(90", angle_mode="DEG"), 0.5)  # auto-close parens

    try:
        evaluate("1 / 0")
        raise AssertionError("Expected CalcError on 1/0")
    except CalcError:
        pass

    assert format_number(1234567.0) == "1,234,567"

    # 2. All 16 Unit Categories round-trip check
    assert len(CATEGORIES) == 16
    for cat in CATEGORIES:
        test_val = 25.0
        mid = convert_value(cat.key, test_val, cat.default_from, cat.default_to)
        back = convert_value(cat.key, mid, cat.default_to, cat.default_from)
        _approx(back, test_val, tol=1e-6)
        all_u = convert_all(cat.key, test_val, cat.default_from)
        assert len(all_u) == len(cat.units)

    # Specific physical benchmark checks
    _approx(convert_value("temperature", 100.0, "C", "F"), 212.0)
    _approx(convert_value("temperature", -40.0, "C", "F"), -40.0)
    _approx(convert_value("temperature", 0.0, "C", "K"), 273.15)
    _approx(convert_value("length", 1.0, "mi", "m"), 1609.344)
    _approx(convert_value("fuel", 5.0, "l100", "kml"), 20.0)
    _approx(convert_value("data", 1.0, "GiB", "MB"), float(1024 ** 3) / 1e6)

    # 3. Solvers & Utilities
    q_res = dict(solve_quadratic(1, -5, 6))
    assert q_res["Root x₁"] == "3" and q_res["Root x₂"] == "2"

    c_res = dict(solve_cubic(1, -6, 11, -6))
    roots_set = {c_res["Root x₁"], c_res["Root x₂"], c_res["Root x₃"]}
    assert roots_set == {"1", "2", "3"}

    lin_res = dict(solve_linear_system([[2, 3], [5, -1]], [13, 7]))
    assert lin_res["x"] == "2" and lin_res["y"] == "3"

    st_res = dict(compute_statistics("2, 4, 4, 4, 5, 5, 7, 9"))
    assert st_res["Mean (μ)"] == "5" and st_res["Pop. Std Dev (σ)"] == "2"

    fin = compute_loan_and_compound(12000, 0.0, 1.0, 12)
    assert dict(fin["loan"])["Monthly Payment (EMI)"] == "1,000"

    dd = dict(compute_date_diff("2026-01-01", "2026-01-11"))
    assert dd["Total Days"] == "10 days"

    bmi = dict(compute_bmi(70.0, 175.0))
    assert "Normal" in bmi["WHO Category"]

    print("ALL PRISM CALC TESTS PASSED!")


if __name__ == "__main__":
    run_all_tests()
