"""Safe recursive-descent scientific expression parser, constants, and number formatting."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple


class CalcError(Exception):
    """User-facing mathematical or syntax error."""


@dataclass(frozen=True)
class ConstantInfo:
    key: str
    symbol: str
    name: str
    value: float
    unit: str


PHYSICAL_CONSTANTS: List[ConstantInfo] = [
    ConstantInfo("pi", "π", "Archimedes' Constant (Pi)", math.pi, ""),
    ConstantInfo("e", "e", "Euler's Number", math.e, ""),
    ConstantInfo("tau", "τ", "Circle Constant (2π)", math.tau, ""),
    ConstantInfo("phi", "φ", "Golden Ratio", (1.0 + math.sqrt(5.0)) / 2.0, ""),
    ConstantInfo("c", "c", "Speed of Light in Vacuum", 299_792_458.0, "m/s"),
    ConstantInfo("g0", "g", "Standard Gravity", 9.80665, "m/s²"),
    ConstantInfo("G", "G", "Newtonian Gravitational Constant", 6.67430e-11, "m³/(kg·s²)"),
    ConstantInfo("h", "h", "Planck Constant", 6.62607015e-34, "J·s"),
    ConstantInfo("hbar", "ℏ", "Reduced Planck Constant", 1.054571817e-34, "J·s"),
    ConstantInfo("NA", "Nₐ", "Avogadro Constant", 6.02214076e23, "mol⁻¹"),
    ConstantInfo("kB", "k_B", "Boltzmann Constant", 1.380649e-23, "J/K"),
    ConstantInfo("R", "R", "Molar Gas Constant", 8.314462618, "J/(mol·K)"),
    ConstantInfo("qe", "q_e", "Elementary Charge", 1.602176634e-19, "C"),
    ConstantInfo("me", "m_e", "Electron Mass", 9.1093837015e-31, "kg"),
    ConstantInfo("mp", "m_p", "Proton Mass", 1.67262192369e-27, "kg"),
    ConstantInfo("eps0", "ε₀", "Vacuum Permittivity", 8.8541878128e-12, "F/m"),
]

CONSTANTS_MAP: Dict[str, float] = {c.key: c.value for c in PHYSICAL_CONSTANTS}


def format_number(value: float, sci_notation: bool = False, precision: int = 12) -> str:
    """Format a float cleanly without ugly binary floating-point tails."""
    if math.isnan(value):
        return "NaN"
    if math.isinf(value):
        return "∞" if value > 0 else "-∞"
    if abs(value) < 1e-15:
        value = 0.0

    if sci_notation:
        if value == 0.0:
            return "0.000000e+00"
        return f"{value:.{max(2, min(10, precision - 2))}e}"

    abs_v = abs(value)
    if abs_v != 0.0 and (abs_v >= 10 ** precision or abs_v < 1e-6):
        s = f"{value:.{max(4, precision - 4)}e}"
        mant, exp = s.split("e")
        mant = mant.rstrip("0").rstrip(".")
        exp_int = int(exp)
        sign = "+" if exp_int >= 0 else ""
        return f"{mant}e{sign}{exp_int}"

    # Snap near-integers within 1e-12
    nearest = round(value)
    if abs_v < 1e15 and abs(value - nearest) <= max(1e-12, abs_v * 1e-14):
        return f"{int(nearest):,}"

    text = f"{value:.{precision}g}"
    if "e" in text or "E" in text:
        return text
    if "." in text:
        int_part, dec_part = text.split(".", 1)
        dec_part = dec_part.rstrip("0")
        neg = int_part.startswith("-")
        digits = int_part[1:] if neg else int_part
        if digits.isdigit():
            int_fmt = f"{int(digits):,}"
            if neg:
                int_fmt = "-" + int_fmt
        else:
            int_fmt = int_part
        return f"{int_fmt}.{dec_part}" if dec_part else int_fmt

    neg = text.startswith("-")
    digits = text[1:] if neg else text
    if digits.isdigit():
        return ("-" if neg else "") + f"{int(digits):,}"
    return text


def format_plain(value: float, precision: int = 10) -> str:
    """Format a float without commas (suitable for inserting back into an Entry)."""
    return format_number(value, sci_notation=False, precision=precision).replace(",", "")


@dataclass(frozen=True)
class _Token:
    kind: str  # NUM, IDENT, OP, LPAREN, RPAREN, COMMA, PREFIX_RAD, EOF
    value: object


_INFIX_IDENTS = {"mod", "ncr", "npr", "yroot"}


def _to_radians(angle: float, angle_mode: str) -> float:
    mode = angle_mode.upper()
    if mode == "DEG":
        return math.radians(angle)
    if mode == "GRAD":
        return angle * (math.pi / 200.0)
    return angle


def _from_radians(rad: float, angle_mode: str) -> float:
    mode = angle_mode.upper()
    if mode == "DEG":
        return math.degrees(rad)
    if mode == "GRAD":
        return rad * (200.0 / math.pi)
    return rad


def _clean_sin(angle: float, angle_mode: str) -> float:
    mode = angle_mode.upper()
    if mode == "DEG" and abs(angle % 180.0) < 1e-12:
        return 0.0
    if mode == "GRAD" and abs(angle % 200.0) < 1e-12:
        return 0.0
    val = math.sin(_to_radians(angle, mode))
    return 0.0 if abs(val) < 1e-15 else val


def _clean_cos(angle: float, angle_mode: str) -> float:
    mode = angle_mode.upper()
    if mode == "DEG" and abs((angle - 90.0) % 180.0) < 1e-12:
        return 0.0
    if mode == "GRAD" and abs((angle - 100.0) % 200.0) < 1e-12:
        return 0.0
    val = math.cos(_to_radians(angle, mode))
    return 0.0 if abs(val) < 1e-15 else val


def _clean_tan(angle: float, angle_mode: str) -> float:
    c = _clean_cos(angle, angle_mode)
    if abs(c) < 1e-14:
        raise CalcError("Domain error: tan undefined")
    s = _clean_sin(angle, angle_mode)
    return s / c


def _safe_factorial(x: float) -> float:
    if x < 0:
        if abs(x - round(x)) < 1e-12:
            raise CalcError("Domain error: factorial of negative integer")
    if abs(x - round(x)) < 1e-12:
        n = int(round(x))
        if n > 170:
            raise CalcError("Overflow: factorial exceeds 170!")
        return float(math.factorial(n))
    try:
        return math.gamma(x + 1.0)
    except (ValueError, OverflowError) as exc:
        raise CalcError("Math overflow or domain error in Gamma") from exc


def _safe_ncr(n_val: float, r_val: float) -> float:
    if abs(n_val - round(n_val)) > 1e-9 or abs(r_val - round(r_val)) > 1e-9:
        raise CalcError("nCr requires integer arguments")
    n, r = int(round(n_val)), int(round(r_val))
    if n < 0 or r < 0 or r > n:
        raise CalcError("Domain error: require 0 ≤ r ≤ n")
    if n > 1000:
        raise CalcError("Overflow in nCr")
    return float(math.comb(n, r))


def _safe_npr(n_val: float, r_val: float) -> float:
    if abs(n_val - round(n_val)) > 1e-9 or abs(r_val - round(r_val)) > 1e-9:
        raise CalcError("nPr requires integer arguments")
    n, r = int(round(n_val)), int(round(r_val))
    if n < 0 or r < 0 or r > n:
        raise CalcError("Domain error: require 0 ≤ r ≤ n")
    if n > 1000:
        raise CalcError("Overflow in nPr")
    return float(math.perm(n, r))


def _safe_power(base: float, exp: float) -> float:
    if base == 0.0 and exp < 0.0:
        raise CalcError("Division by zero (0 to negative power)")
    if base < 0.0 and abs(exp - round(exp)) > 1e-12:
        raise CalcError("Domain error: negative base with fractional exponent")
    try:
        res = math.pow(base, round(exp) if base < 0.0 else exp)
    except OverflowError as exc:
        raise CalcError("Overflow error") from exc
    except ValueError as exc:
        raise CalcError("Domain error in power") from exc
    if math.isinf(res):
        raise CalcError("Overflow error")
    return res


def _safe_yroot(degree: float, radicand: float) -> float:
    if abs(degree) < 1e-15:
        raise CalcError("Domain error: 0th root undefined")
    if radicand < 0.0:
        if abs(degree - round(degree)) < 1e-12 and int(round(degree)) % 2 == 1:
            return -_safe_power(-radicand, 1.0 / round(degree))
        raise CalcError("Domain error: even root of negative number")
    return _safe_power(radicand, 1.0 / degree)


def build_functions(angle_mode: str = "DEG") -> Dict[str, Tuple[int, Callable[..., float]]]:
    """Return mapping of lowercase function name -> (arity, callable). arity=-1 means variadic."""

    def _asin(x: float) -> float:
        if x < -1.0 or x > 1.0:
            raise CalcError("Domain error: asin expects [-1, 1]")
        return _from_radians(math.asin(x), angle_mode)

    def _acos(x: float) -> float:
        if x < -1.0 or x > 1.0:
            raise CalcError("Domain error: acos expects [-1, 1]")
        return _from_radians(math.acos(x), angle_mode)

    def _atan(x: float) -> float:
        return _from_radians(math.atan(x), angle_mode)

    def _atan2(y: float, x: float) -> float:
        return _from_radians(math.atan2(y, x), angle_mode)

    def _acosh(x: float) -> float:
        if x < 1.0:
            raise CalcError("Domain error: acosh expects x ≥ 1")
        return math.acosh(x)

    def _atanh(x: float) -> float:
        if x <= -1.0 or x >= 1.0:
            raise CalcError("Domain error: atanh expects (-1, 1)")
        return math.atanh(x)

    def _ln(x: float) -> float:
        if x <= 0.0:
            raise CalcError("Domain error: ln expects x > 0")
        return math.log(x)

    def _log10(x: float) -> float:
        if x <= 0.0:
            raise CalcError("Domain error: log expects x > 0")
        return math.log10(x)

    def _log2(x: float) -> float:
        if x <= 0.0:
            raise CalcError("Domain error: log2 expects x > 0")
        return math.log2(x)

    def _log_base(x: float, base: float = 10.0) -> float:
        if x <= 0.0 or base <= 0.0 or abs(base - 1.0) < 1e-15:
            raise CalcError("Domain error in logarithm")
        return math.log(x, base)

    def _sqrt(x: float) -> float:
        if x < 0.0:
            raise CalcError("Domain error: √ of negative number")
        return math.sqrt(x)

    def _cbrt(x: float) -> float:
        return math.copysign(abs(x) ** (1.0 / 3.0), x)

    def _sec(x: float) -> float:
        c = _clean_cos(x, angle_mode)
        if abs(c) < 1e-14:
            raise CalcError("Domain error: sec undefined")
        return 1.0 / c

    def _csc(x: float) -> float:
        s = _clean_sin(x, angle_mode)
        if abs(s) < 1e-14:
            raise CalcError("Domain error: csc undefined")
        return 1.0 / s

    def _cot(x: float) -> float:
        s = _clean_sin(x, angle_mode)
        if abs(s) < 1e-14:
            raise CalcError("Domain error: cot undefined")
        return _clean_cos(x, angle_mode) / s

    def _exp(x: float) -> float:
        try:
            return math.exp(x)
        except OverflowError as exc:
            raise CalcError("Overflow in exp") from exc

    def _gcd(*vals: float) -> float:
        if len(vals) < 2:
            raise CalcError("gcd requires at least 2 integers")
        ints = []
        for v in vals:
            if abs(v - round(v)) > 1e-9:
                raise CalcError("gcd requires integers")
            ints.append(int(round(v)))
        return float(math.gcd(*ints))

    def _lcm(*vals: float) -> float:
        if len(vals) < 2:
            raise CalcError("lcm requires at least 2 integers")
        ints = []
        for v in vals:
            if abs(v - round(v)) > 1e-9:
                raise CalcError("lcm requires integers")
            ints.append(int(round(v)))
        return float(math.lcm(*ints))

    return {
        "sin": (1, lambda x: _clean_sin(x, angle_mode)),
        "cos": (1, lambda x: _clean_cos(x, angle_mode)),
        "tan": (1, lambda x: _clean_tan(x, angle_mode)),
        "asin": (1, _asin),
        "arcsin": (1, _asin),
        "acos": (1, _acos),
        "arccos": (1, _acos),
        "atan": (1, _atan),
        "arctan": (1, _atan),
        "atan2": (2, _atan2),
        "sec": (1, _sec),
        "csc": (1, _csc),
        "cot": (1, _cot),
        "sinh": (1, math.sinh),
        "cosh": (1, math.cosh),
        "tanh": (1, math.tanh),
        "asinh": (1, math.asinh),
        "acosh": (1, _acosh),
        "atanh": (1, _atanh),
        "ln": (1, _ln),
        "log": (-1, _log_base),
        "log10": (1, _log10),
        "log2": (1, _log2),
        "exp": (1, _exp),
        "sqrt": (1, _sqrt),
        "cbrt": (1, _cbrt),
        "root": (2, _safe_yroot),
        "abs": (1, abs),
        "floor": (1, lambda x: float(math.floor(x))),
        "ceil": (1, lambda x: float(math.ceil(x))),
        "round": (1, lambda x: float(round(x))),
        "sign": (1, lambda x: 0.0 if x == 0 else math.copysign(1.0, x)),
        "fact": (1, _safe_factorial),
        "ncr": (2, _safe_ncr),
        "npr": (2, _safe_npr),
        "gcd": (-1, _gcd),
        "lcm": (-1, _lcm),
        "deg": (1, math.degrees),
        "rad": (1, math.radians),
        "hypot": (-1, lambda *xs: math.hypot(*xs)),
        "min": (-1, lambda *xs: min(xs)),
        "max": (-1, lambda *xs: max(xs)),
        "rand": (0, random.random),
    }


def tokenize(expr: str, known_functions: set) -> List[_Token]:
    s = expr.strip()
    if not s:
        raise CalcError("Empty expression")

    # Normalize pretty math glyphs
    replacements = (
        ("×", "*"),
        ("·", "*"),
        ("÷", "/"),
        ("−", "-"),
        ("–", "-"),
        ("**", "^"),
        ("π", " pi "),
        ("τ", " tau "),
        ("φ", " phi "),
        ("ℏ", " hbar "),
        ("²", "^2"),
        ("³", "^3"),
    )
    for src, dst in replacements:
        s = s.replace(src, dst)

    raw: List[_Token] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch.isspace():
            i += 1
            continue
        if ch == "√":
            raw.append(_Token("PREFIX_RAD", "sqrt"))
            i += 1
            continue
        if ch == "∛":
            raw.append(_Token("PREFIX_RAD", "cbrt"))
            i += 1
            continue
        if ch.isdigit() or (ch == "." and i + 1 < n and s[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < n and (s[i].isdigit() or (s[i] == "." and not has_dot)):
                if s[i] == ".":
                    has_dot = True
                i += 1
            # Scientific notation literal e.g. 6.022e23 or 1.5e-4
            if i < n and s[i] in ("e", "E"):
                j = i + 1
                if j < n and s[j] in ("+", "-"):
                    j += 1
                if j < n and s[j].isdigit():
                    i = j
                    while i < n and s[i].isdigit():
                        i += 1
            num_str = s[start:i]
            try:
                raw.append(_Token("NUM", float(num_str)))
            except ValueError as exc:
                raise CalcError(f"Invalid number '{num_str}'") from exc
            continue
        if ch.isalpha() or ch == "_":
            start = i
            while i < n and (s[i].isalnum() or s[i] == "_"):
                i += 1
            raw.append(_Token("IDENT", s[start:i]))
            continue
        if ch == "(":
            raw.append(_Token("LPAREN", "("))
            i += 1
            continue
        if ch == ")":
            raw.append(_Token("RPAREN", ")"))
            i += 1
            continue
        if ch == ",":
            raw.append(_Token("COMMA", ","))
            i += 1
            continue
        if ch in "+-*/^!%":
            raw.append(_Token("OP", ch))
            i += 1
            continue
        raise CalcError(f"Unexpected character '{ch}'")

    # Auto-balance unclosed '(' at end of expression
    open_parens = sum(1 for t in raw if t.kind == "LPAREN") - sum(1 for t in raw if t.kind == "RPAREN")
    if open_parens < 0:
        raise CalcError("Unmatched ')'")
    for _ in range(open_parens):
        raw.append(_Token("RPAREN", ")"))

    # Insert implicit '*' where mathematically natural
    out: List[_Token] = []
    for idx, tok in enumerate(raw):
        if out:
            prev = out[-1]
            prev_ends_term = (
                prev.kind in ("NUM", "RPAREN")
                or (prev.kind == "OP" and prev.value == "!")
                or (
                    prev.kind == "IDENT"
                    and str(prev.value).lower() not in known_functions
                    and str(prev.value).lower() not in _INFIX_IDENTS
                )
            )
            curr_starts_term = (
                tok.kind in ("LPAREN", "PREFIX_RAD")
                or (
                    tok.kind == "IDENT"
                    and str(tok.value).lower() not in _INFIX_IDENTS
                )
                or (tok.kind == "NUM" and prev.kind != "NUM")
            )
            if prev_ends_term and curr_starts_term:
                out.append(_Token("OP", "*"))
        out.append(tok)

    out.append(_Token("EOF", None))
    return out


class _Parser:
    def __init__(
        self,
        tokens: List[_Token],
        functions: Dict[str, Tuple[int, Callable[..., float]]],
        variables: Dict[str, float],
    ) -> None:
        self.tokens = tokens
        self.pos = 0
        self.functions = functions
        self.variables = variables

    def peek(self) -> _Token:
        return self.tokens[self.pos]

    def consume(self) -> _Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self) -> float:
        val = self.parse_add()
        if self.peek().kind != "EOF":
            raise CalcError(f"Unexpected '{self.peek().value}'")
        return val

    def parse_add(self) -> float:
        left = self.parse_mul()
        while self.peek().kind == "OP" and self.peek().value in ("+", "-"):
            op = self.consume().value
            right = self.parse_mul()
            left = left + right if op == "+" else left - right
        return left

    def parse_mul(self) -> float:
        left = self.parse_unary()
        while True:
            tok = self.peek()
            if tok.kind == "OP" and tok.value in ("*", "/"):
                op = self.consume().value
                right = self.parse_unary()
                if op == "*":
                    left *= right
                else:
                    if abs(right) < 1e-300:
                        raise CalcError("Division by zero")
                    left /= right
            elif tok.kind == "IDENT" and str(tok.value).lower() in ("mod", "ncr", "npr"):
                op_name = str(self.consume().value).lower()
                right = self.parse_unary()
                if op_name == "mod":
                    if abs(right) < 1e-300:
                        raise CalcError("Modulo by zero")
                    left = left % right
                elif op_name == "ncr":
                    left = _safe_ncr(left, right)
                else:
                    left = _safe_npr(left, right)
            elif tok.kind == "OP" and tok.value == "%":
                # Distinguish binary '17 % 5' vs postfix '50%'
                nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else _Token("EOF", None)
                if nxt.kind in ("NUM", "IDENT", "LPAREN", "PREFIX_RAD") or (
                    nxt.kind == "OP" and nxt.value in ("+", "-") and self.pos + 2 < len(self.tokens)
                ):
                    # Wait: '50% + 1' should be '0.5 + 1', NOT '50 % (+1)'!
                    # Only treat '%' as binary modulo when followed directly by NUM, IDENT, LPAREN, or PREFIX_RAD.
                    if nxt.kind in ("NUM", "IDENT", "LPAREN", "PREFIX_RAD"):
                        self.consume()
                        right = self.parse_unary()
                        if abs(right) < 1e-300:
                            raise CalcError("Modulo by zero")
                        left = left % right
                        continue
                break
            else:
                break
        return left

    def parse_unary(self) -> float:
        tok = self.peek()
        if tok.kind == "OP" and tok.value in ("+", "-"):
            op = self.consume().value
            val = self.parse_unary()
            return -val if op == "-" else val
        if tok.kind == "PREFIX_RAD":
            fn_name = str(self.consume().value)
            val = self.parse_unary()
            _, fn = self.functions[fn_name]
            return fn(val)
        return self.parse_pow()

    def parse_pow(self) -> float:
        base = self.parse_postfix()
        tok = self.peek()
        if tok.kind == "OP" and tok.value == "^":
            self.consume()
            exp = self.parse_unary()
            return _safe_power(base, exp)
        if tok.kind == "IDENT" and str(tok.value).lower() == "yroot":
            self.consume()
            rad = self.parse_unary()
            return _safe_yroot(base, rad)
        return base

    def parse_postfix(self) -> float:
        val = self.parse_primary()
        while self.peek().kind == "OP" and self.peek().value in ("!", "%"):
            nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else _Token("EOF", None)
            if self.peek().value == "%" and nxt.kind in ("NUM", "IDENT", "LPAREN", "PREFIX_RAD"):
                # Let parse_mul handle binary 'a % b'
                break
            op = self.consume().value
            if op == "!":
                val = _safe_factorial(val)
            else:
                val = val / 100.0
        return val

    def parse_primary(self) -> float:
        tok = self.peek()
        if tok.kind == "NUM":
            self.consume()
            return float(tok.value)
        if tok.kind == "LPAREN":
            self.consume()
            val = self.parse_add()
            if self.peek().kind != "RPAREN":
                raise CalcError("Expected ')'")
            self.consume()
            return val
        if tok.kind == "IDENT":
            ident = str(self.consume().value)
            low = ident.lower()
            if self.peek().kind == "LPAREN" and low in self.functions:
                self.consume()  # '('
                args: List[float] = []
                if self.peek().kind != "RPAREN":
                    args.append(self.parse_add())
                    while self.peek().kind == "COMMA":
                        self.consume()
                        args.append(self.parse_add())
                if self.peek().kind != "RPAREN":
                    raise CalcError(f"Expected ')' after {ident}(...")
                self.consume()
                arity, fn = self.functions[low]
                if arity >= 0 and len(args) != arity:
                    raise CalcError(f"{ident}() expects {arity} arg(s), got {len(args)}")
                if arity == -1 and len(args) == 0:
                    raise CalcError(f"{ident}() expects at least 1 argument")
                try:
                    return float(fn(*args))
                except CalcError:
                    raise
                except ZeroDivisionError as exc:
                    raise CalcError("Division by zero") from exc
                except OverflowError as exc:
                    raise CalcError("Numeric overflow") from exc
                except ValueError as exc:
                    raise CalcError(f"Domain error in {ident}()") from exc

            # Check case-sensitive physical constants first (e.g. 'G' vs 'g0'), then lowercase
            if ident in self.variables:
                return self.variables[ident]
            if low in self.variables:
                return self.variables[low]
            if ident in CONSTANTS_MAP:
                return CONSTANTS_MAP[ident]
            if low in CONSTANTS_MAP:
                return CONSTANTS_MAP[low]
            if low in self.functions:
                arity, fn = self.functions[low]
                if arity == 0:
                    return float(fn())
                raise CalcError(f"Function '{ident}' requires parentheses")
            raise CalcError(f"Unknown symbol '{ident}'")
        raise CalcError(f"Unexpected '{tok.value}'")


def evaluate(
    expression: str,
    *,
    angle_mode: str = "DEG",
    ans: float = 0.0,
    extra_vars: Optional[Dict[str, float]] = None,
) -> float:
    """Safely evaluate a mathematical expression string."""
    funcs = build_functions(angle_mode)
    vars_map: Dict[str, float] = {"ans": ans, "Ans": ans}
    if extra_vars:
        vars_map.update(extra_vars)
    tokens = tokenize(expression, set(funcs.keys()))
    parser = _Parser(tokens, funcs, vars_map)
    result = parser.parse()
    if math.isnan(result):
        raise CalcError("Result is undefined (NaN)")
    if math.isinf(result):
        raise CalcError("Numeric overflow (∞)")
    return result
