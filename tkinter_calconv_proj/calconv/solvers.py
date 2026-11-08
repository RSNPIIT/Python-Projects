"""Engineering & everyday math utilities: Equations, Linear Systems, Stats, Finance, Date & BMI."""

from __future__ import annotations

import cmath
import datetime as dt
import math
import re
from collections import Counter
from typing import Dict, List, Tuple

from .evaluator import format_number


def _fmt_complex(z: complex) -> str:
    re_part = 0.0 if abs(z.real) < 1e-12 else z.real
    im_part = 0.0 if abs(z.imag) < 1e-12 else z.imag
    if im_part == 0.0:
        return format_number(re_part, precision=10)
    im_abs = format_number(abs(im_part), precision=8)
    sign = "+" if im_part >= 0 else "-"
    if re_part == 0.0:
        return f"{'-' if im_part < 0 else ''}{im_abs}i"
    return f"{format_number(re_part, precision=8)} {sign} {im_abs}i"


def solve_quadratic(a: float, b: float, c: float) -> List[Tuple[str, str]]:
    """Solve a·x² + b·x + c = 0 (degenerates gracefully if a == 0)."""
    if abs(a) < 1e-15:
        if abs(b) < 1e-15:
            return [("Status", "Infinite solutions (0 = 0)" if abs(c) < 1e-15 else "No solution (inconsistent)")]
        x = -c / b
        return [
            ("Equation Type", "Linear (a = 0)"),
            ("x", format_number(x, precision=10)),
        ]

    disc = b * b - 4.0 * a * c
    vx = -b / (2.0 * a)
    vy = a * vx * vx + b * vx + c
    if disc > 1e-14:
        sq = math.sqrt(disc)
        x1 = (-b + sq) / (2.0 * a)
        x2 = (-b - sq) / (2.0 * a)
        nature = "Two distinct real roots (Δ > 0)"
        r1, r2 = format_number(x1, precision=10), format_number(x2, precision=10)
    elif abs(disc) <= 1e-14:
        x1 = -b / (2.0 * a)
        nature = "One repeated real root (Δ = 0)"
        r1 = r2 = format_number(x1, precision=10)
    else:
        sq = cmath.sqrt(disc)
        z1 = (-b + sq) / (2.0 * a)
        z2 = (-b - sq) / (2.0 * a)
        nature = "Complex conjugate roots (Δ < 0)"
        r1, r2 = _fmt_complex(z1), _fmt_complex(z2)

    return [
        ("Nature", nature),
        ("Discriminant (Δ)", format_number(disc, precision=10)),
        ("Root x₁", r1),
        ("Root x₂", r2),
        ("Vertex (h, k)", f"({format_number(vx, precision=8)}, {format_number(vy, precision=8)})"),
    ]


def solve_cubic(a: float, b: float, c: float, d: float) -> List[Tuple[str, str]]:
    """Solve a·x³ + b·x² + c·x + d = 0 using depressed-cubic Cardano/Vieta formulas."""
    if abs(a) < 1e-15:
        return solve_quadratic(b, c, d)

    # Normalize: x³ + B·x² + C·x + D = 0
    B, C, D = b / a, c / a, d / a
    shift = B / 3.0
    p = C - (B * B) / 3.0
    q = (2.0 * B * B * B) / 27.0 - (B * C) / 3.0 + D
    disc = (q / 2.0) ** 2 + (p / 3.0) ** 3

    roots: List[complex] = []
    if disc > 1e-14:
        sq = math.sqrt(disc)
        u = math.copysign(abs(-q / 2.0 + sq) ** (1.0 / 3.0), -q / 2.0 + sq)
        v = math.copysign(abs(-q / 2.0 - sq) ** (1.0 / 3.0), -q / 2.0 - sq)
        t1 = u + v
        re_conj = -(u + v) / 2.0
        im_conj = (math.sqrt(3.0) / 2.0) * (u - v)
        roots = [
            complex(t1 - shift, 0.0),
            complex(re_conj - shift, im_conj),
            complex(re_conj - shift, -im_conj),
        ]
        nature = "1 real root & 2 complex conjugate roots"
    elif abs(disc) <= 1e-14:
        if abs(p) < 1e-14 and abs(q) < 1e-14:
            roots = [complex(-shift, 0.0)] * 3
            nature = "Triple repeated real root"
        else:
            u = math.copysign(abs(-q / 2.0) ** (1.0 / 3.0), -q / 2.0)
            roots = [complex(2.0 * u - shift, 0.0), complex(-u - shift, 0.0), complex(-u - shift, 0.0)]
            nature = "3 real roots (at least two equal)"
    else:
        r = math.sqrt(max(0.0, -(p / 3.0) ** 3))
        cos_arg = max(-1.0, min(1.0, -q / (2.0 * r))) if r > 0 else 0.0
        phi = math.acos(cos_arg)
        m = 2.0 * math.sqrt(-p / 3.0)
        roots = [
            complex(m * math.cos((phi + 2.0 * math.pi * k) / 3.0) - shift, 0.0)
            for k in range(3)
        ]
        nature = "3 distinct real roots"

    return [
        ("Nature", nature),
        ("Root x₁", _fmt_complex(roots[0])),
        ("Root x₂", _fmt_complex(roots[1])),
        ("Root x₃", _fmt_complex(roots[2])),
    ]


def solve_linear_system(matrix: List[List[float]], rhs: List[float]) -> List[Tuple[str, str]]:
    """Solve an n×n linear system Ax = b with partial pivoting."""
    n = len(rhs)
    aug = [list(map(float, matrix[i])) + [float(rhs[i])] for i in range(n)]

    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot_row][col]) < 1e-13:
            return [("Status", "Singular matrix — no unique solution (det = 0)")]
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]

        piv = aug[col][col]
        for j in range(col, n + 1):
            aug[col][j] /= piv

        for r in range(n):
            if r != col:
                factor = aug[r][col]
                for j in range(col, n + 1):
                    aug[r][j] -= factor * aug[col][j]

    names = ["x", "y", "z", "w"]
    out = [("Status", f"Unique {n}×{n} solution found")]
    for i in range(n):
        out.append((names[i], format_number(aug[i][n], precision=10)))
    return out


def compute_statistics(raw_text: str) -> List[Tuple[str, str]]:
    """Parse comma/whitespace separated numbers and return descriptive statistics."""
    parts = [p for p in re.split(r"[\s,;]+", raw_text.strip()) if p]
    if not parts:
        raise ValueError("Enter at least one number")
    nums = [float(p) for p in parts]
    n = len(nums)
    s_nums = sorted(nums)
    total = sum(nums)
    mean = total / n

    if n % 2 == 1:
        median = s_nums[n // 2]
    else:
        median = 0.5 * (s_nums[n // 2 - 1] + s_nums[n // 2])

    counts = Counter(nums)
    max_freq = max(counts.values())
    if max_freq == 1:
        mode_str = "No repeats (all unique)"
    else:
        modes = sorted(k for k, v in counts.items() if v == max_freq)
        mode_str = ", ".join(format_number(m, precision=8) for m in modes[:4]) + f"  (×{max_freq})"

    pop_var = sum((x - mean) ** 2 for x in nums) / n
    pop_sd = math.sqrt(pop_var)
    samp_var = sum((x - mean) ** 2 for x in nums) / (n - 1) if n > 1 else 0.0
    samp_sd = math.sqrt(samp_var)

    def _percentile(p: float) -> float:
        if n == 1:
            return s_nums[0]
        idx = p * (n - 1)
        lo = int(math.floor(idx))
        hi = min(n - 1, lo + 1)
        frac = idx - lo
        return s_nums[lo] + (s_nums[hi] - s_nums[lo]) * frac

    q1 = _percentile(0.25)
    q3 = _percentile(0.75)
    iqr = q3 - q1

    rows = [
        ("Count (n)", str(n)),
        ("Sum (Σx)", format_number(total, precision=10)),
        ("Mean (μ)", format_number(mean, precision=10)),
        ("Median", format_number(median, precision=10)),
        ("Mode", mode_str),
        ("Sample Std Dev (s)", format_number(samp_sd, precision=10) if n > 1 else "—"),
        ("Pop. Std Dev (σ)", format_number(pop_sd, precision=10)),
        ("Sample Variance (s²)", format_number(samp_var, precision=10) if n > 1 else "—"),
        ("Min / Max", f"{format_number(s_nums[0], precision=8)}  /  {format_number(s_nums[-1], precision=8)}"),
        ("Range", format_number(s_nums[-1] - s_nums[0], precision=10)),
        ("Quartiles Q₁ / Q₃ (IQR)", f"{format_number(q1, precision=8)} / {format_number(q3, precision=8)}  (IQR {format_number(iqr, precision=8)})"),
    ]
    if all(x > 0 for x in nums):
        geo = math.exp(sum(math.log(x) for x in nums) / n)
        harm = n / sum(1.0 / x for x in nums)
        rows.append(("Geometric / Harmonic Mean", f"{format_number(geo, precision=8)}  /  {format_number(harm, precision=8)}"))
    return rows


def compute_loan_and_compound(
    principal: float,
    annual_rate_pct: float,
    years: float,
    compounds_per_year: int = 12,
) -> Dict[str, List[Tuple[str, str]]]:
    """Compute both Loan Amortization (EMI) and Compound Growth for given parameters."""
    if principal < 0 or years <= 0 or compounds_per_year <= 0:
        raise ValueError("Principal ≥ 0 and Years > 0 required")

    months = max(1, int(round(years * 12)))
    r_month = (annual_rate_pct / 100.0) / 12.0
    if abs(r_month) < 1e-12:
        emi = principal / months
    else:
        factor = (1.0 + r_month) ** months
        emi = principal * r_month * factor / (factor - 1.0)
    total_paid = emi * months
    total_interest = total_paid - principal

    r_comp = (annual_rate_pct / 100.0) / compounds_per_year
    n_periods = years * compounds_per_year
    future_val = principal * ((1.0 + r_comp) ** n_periods)
    comp_gain = future_val - principal

    return {
        "loan": [
            ("Monthly Payment (EMI)", format_number(emi, precision=8)),
            ("Total Principal", format_number(principal, precision=10)),
            ("Total Interest Paid", format_number(total_interest, precision=10)),
            ("Total Repayment", format_number(total_paid, precision=10)),
            ("Term Length", f"{months} months ({format_number(years, precision=4)} yrs)"),
        ],
        "compound": [
            ("Future Value (FV)", format_number(future_val, precision=10)),
            ("Compound Interest Earned", format_number(comp_gain, precision=10)),
            ("Growth Multiple", f"{format_number(future_val / principal, precision=6)}×" if principal > 0 else "—"),
        ],
    }


def compute_date_diff(d1_str: str, d2_str: str) -> List[Tuple[str, str]]:
    """Compute exact Y/M/D span, total days, weeks, workdays, and hours between two YYYY-MM-DD dates."""
    d1 = dt.date.fromisoformat(d1_str.strip())
    d2 = dt.date.fromisoformat(d2_str.strip())
    start, end = (d1, d2) if d1 <= d2 else (d2, d1)
    total_days = (end - start).days

    years = end.year - start.year
    months = end.month - start.month
    days = end.day - start.day
    if days < 0:
        months -= 1
        prev_month_end = end.replace(day=1) - dt.timedelta(days=1)
        days += prev_month_end.day
    if months < 0:
        years -= 1
        months += 12

    weeks, rem_days = divmod(total_days, 7)
    # Exact weekday count in O(1)
    full_workdays = weeks * 5
    extra_workdays = sum(1 for i in range(rem_days) if (start + dt.timedelta(days=i)).weekday() < 5)
    workdays = full_workdays + extra_workdays

    return [
        ("Calendar Span", f"{years} yr, {months} mo, {days} day(s)"),
        ("Total Days", f"{total_days:,} days"),
        ("Weeks + Days", f"{weeks:,} weeks, {rem_days} days"),
        ("Business Days (Mon–Fri)", f"{workdays:,} days"),
        ("Total Hours / Minutes", f"{total_days * 24:,} hrs  /  {total_days * 1440:,} min"),
    ]


def compute_bmi(weight_kg: float, height_cm: float) -> List[Tuple[str, str]]:
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("Weight and height must be positive")
    h_m = height_cm / 100.0
    bmi = weight_kg / (h_m * h_m)
    if bmi < 18.5:
        cat = "Underweight (< 18.5)"
    elif bmi < 25.0:
        cat = "Normal / Healthy (18.5 – 24.9)"
    elif bmi < 30.0:
        cat = "Overweight (25.0 – 29.9)"
    else:
        cat = "Obese (≥ 30.0)"
    min_healthy = 18.5 * h_m * h_m
    max_healthy = 24.9 * h_m * h_m
    return [
        ("BMI Score", format_number(bmi, precision=4)),
        ("WHO Category", cat),
        ("Healthy Weight Range", f"{format_number(min_healthy, precision=4)} kg – {format_number(max_healthy, precision=4)} kg"),
        ("Imperial Equivalent", f"{format_number(weight_kg * 2.20462262, precision=4)} lb  ·  {int((height_cm / 2.54) // 12)}'{round((height_cm / 2.54) % 12)}\""),
    ]
