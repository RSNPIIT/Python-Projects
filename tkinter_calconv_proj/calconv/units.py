"""Comprehensive 16-category, 150+ unit exact bidirectional measurement converter."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class UnitDef:
    code: str
    name: str
    symbol: str
    to_base: Callable[[float], float]
    from_base: Callable[[float], float]


def _lin(code: str, name: str, symbol: str, factor: float) -> UnitDef:
    """Create a linear unit where 1 unit = `factor` base units."""
    return UnitDef(
        code=code,
        name=name,
        symbol=symbol,
        to_base=lambda v, f=factor: v * f,
        from_base=lambda b, f=factor: b / f,
    )


@dataclass(frozen=True)
class CategoryDef:
    key: str
    name: str
    badge: str
    base_unit: str
    default_from: str
    default_to: str
    units: List[UnitDef]


CATEGORIES: List[CategoryDef] = [
    # 1. Length & Distance (base: meter)
    CategoryDef(
        key="length",
        name="Length & Distance",
        badge="📏",
        base_unit="m",
        default_from="km",
        default_to="mi",
        units=[
            _lin("nm", "Nanometer", "nm", 1e-9),
            _lin("um", "Micrometer", "µm", 1e-6),
            _lin("mm", "Millimeter", "mm", 1e-3),
            _lin("cm", "Centimeter", "cm", 1e-2),
            _lin("dm", "Decimeter", "dm", 1e-1),
            _lin("m", "Meter", "m", 1.0),
            _lin("km", "Kilometer", "km", 1e3),
            _lin("in", "Inch", "in", 0.0254),
            _lin("ft", "Foot", "ft", 0.3048),
            _lin("yd", "Yard", "yd", 0.9144),
            _lin("mi", "Mile", "mi", 1609.344),
            _lin("nmi", "Nautical Mile", "nmi", 1852.0),
            _lin("ang", "Angstrom", "Å", 1e-10),
            _lin("au", "Astronomical Unit", "AU", 149_597_870_700.0),
            _lin("ly", "Light-Year", "ly", 9_460_730_472_580_800.0),
        ],
    ),
    # 2. Mass & Weight (base: kilogram)
    CategoryDef(
        key="mass",
        name="Mass & Weight",
        badge="⚖️",
        base_unit="kg",
        default_from="kg",
        default_to="lb",
        units=[
            _lin("ug", "Microgram", "µg", 1e-9),
            _lin("mg", "Milligram", "mg", 1e-6),
            _lin("ct", "Metric Carat", "ct", 0.0002),
            _lin("g", "Gram", "g", 1e-3),
            _lin("kg", "Kilogram", "kg", 1.0),
            _lin("t", "Metric Tonne", "t", 1000.0),
            _lin("gr", "Grain", "gr", 6.479891e-5),
            _lin("oz", "Ounce", "oz", 0.028349523125),
            _lin("toz", "Troy Ounce", "oz t", 0.0311034768),
            _lin("lb", "Pound", "lb", 0.45359237),
            _lin("st", "Stone", "st", 6.35029318),
            _lin("ton_us", "US Short Ton", "ton (US)", 907.18474),
            _lin("ton_uk", "Imperial Long Ton", "ton (UK)", 1016.0469088),
        ],
    ),
    # 3. Temperature (base: Kelvin — exact affine formulas)
    CategoryDef(
        key="temperature",
        name="Temperature",
        badge="🌡️",
        base_unit="K",
        default_from="C",
        default_to="F",
        units=[
            UnitDef("C", "Celsius", "°C", lambda c: c + 273.15, lambda k: k - 273.15),
            UnitDef(
                "F",
                "Fahrenheit",
                "°F",
                lambda f: (f - 32.0) * (5.0 / 9.0) + 273.15,
                lambda k: (k - 273.15) * (9.0 / 5.0) + 32.0,
            ),
            UnitDef("K", "Kelvin", "K", lambda k: k, lambda k: k),
            UnitDef("R", "Rankine", "°R", lambda r: r * (5.0 / 9.0), lambda k: k * (9.0 / 5.0)),
            UnitDef(
                "Re",
                "Réaumur",
                "°Ré",
                lambda re: re * 1.25 + 273.15,
                lambda k: (k - 273.15) * 0.8,
            ),
        ],
    ),
    # 4. Area (base: m²)
    CategoryDef(
        key="area",
        name="Area",
        badge="📐",
        base_unit="m2",
        default_from="m2",
        default_to="ft2",
        units=[
            _lin("mm2", "Square Millimeter", "mm²", 1e-6),
            _lin("cm2", "Square Centimeter", "cm²", 1e-4),
            _lin("m2", "Square Meter", "m²", 1.0),
            _lin("are", "Are", "a", 100.0),
            _lin("ha", "Hectare", "ha", 10_000.0),
            _lin("km2", "Square Kilometer", "km²", 1e6),
            _lin("in2", "Square Inch", "in²", 0.00064516),
            _lin("ft2", "Square Foot", "ft²", 0.09290304),
            _lin("yd2", "Square Yard", "yd²", 0.83612736),
            _lin("ac", "Acre", "ac", 4046.8564224),
            _lin("mi2", "Square Mile", "mi²", 2_589_988.110336),
        ],
    ),
    # 5. Volume & Capacity (base: Liter)
    CategoryDef(
        key="volume",
        name="Volume & Capacity",
        badge="🧪",
        base_unit="L",
        default_from="L",
        default_to="gal_us",
        units=[
            _lin("mL", "Milliliter / cm³", "mL", 1e-3),
            _lin("cL", "Centiliter", "cL", 1e-2),
            _lin("L", "Liter", "L", 1.0),
            _lin("m3", "Cubic Meter", "m³", 1000.0),
            _lin("tsp", "US Teaspoon", "tsp", 0.00492892159375),
            _lin("tbsp", "US Tablespoon", "tbsp", 0.01478676478125),
            _lin("floz_us", "US Fluid Ounce", "fl oz", 0.0295735295625),
            _lin("cup_us", "US Cup", "cup", 0.2365882365),
            _lin("pt_us", "US Liquid Pint", "pt", 0.473176473),
            _lin("qt_us", "US Liquid Quart", "qt", 0.946352946),
            _lin("gal_us", "US Liquid Gallon", "gal (US)", 3.785411784),
            _lin("gal_uk", "Imperial Gallon", "gal (UK)", 4.54609),
            _lin("in3", "Cubic Inch", "in³", 0.016387064),
            _lin("ft3", "Cubic Foot", "ft³", 28.316846592),
            _lin("bbl", "Oil Barrel (42 gal)", "bbl", 158.987294928),
        ],
    ),
    # 6. Speed & Velocity (base: m/s)
    CategoryDef(
        key="speed",
        name="Speed & Velocity",
        badge="🚀",
        base_unit="mps",
        default_from="kmh",
        default_to="mph",
        units=[
            _lin("mps", "Meter per Second", "m/s", 1.0),
            _lin("kmh", "Kilometer per Hour", "km/h", 1.0 / 3.6),
            _lin("mph", "Mile per Hour", "mph", 0.44704),
            _lin("fps", "Foot per Second", "ft/s", 0.3048),
            _lin("kn", "Knot (Nautical mph)", "kn", 1852.0 / 3600.0),
            _lin("mach", "Mach (Sea Level 15°C)", "Ma", 340.29),
            _lin("c_spd", "Speed of Light", "c", 299_792_458.0),
        ],
    ),
    # 7. Time (base: second)
    CategoryDef(
        key="time",
        name="Time & Duration",
        badge="⏱️",
        base_unit="s",
        default_from="hr",
        default_to="min",
        units=[
            _lin("ns", "Nanosecond", "ns", 1e-9),
            _lin("us", "Microsecond", "µs", 1e-6),
            _lin("ms", "Millisecond", "ms", 1e-3),
            _lin("s", "Second", "s", 1.0),
            _lin("min", "Minute", "min", 60.0),
            _lin("hr", "Hour", "hr", 3600.0),
            _lin("day", "Day", "d", 86_400.0),
            _lin("wk", "Week", "wk", 604_800.0),
            _lin("mo", "Month (Avg 30.437d)", "mo", 2_629_746.0),
            _lin("yr", "Year (365.25d)", "yr", 31_557_600.0),
            _lin("dec", "Decade", "dec", 315_576_000.0),
            _lin("cen", "Century", "cent", 3_155_760_000.0),
        ],
    ),
    # 8. Digital Storage (base: Byte)
    CategoryDef(
        key="data",
        name="Digital Data Storage",
        badge="💾",
        base_unit="B",
        default_from="GB",
        default_to="GiB",
        units=[
            _lin("bit", "Bit", "b", 0.125),
            _lin("B", "Byte", "B", 1.0),
            _lin("KB", "Kilobyte (10³ B)", "KB", 1e3),
            _lin("KiB", "Kibibyte (2¹⁰ B)", "KiB", float(1024 ** 1)),
            _lin("MB", "Megabyte (10⁶ B)", "MB", 1e6),
            _lin("MiB", "Mebibyte (2²⁰ B)", "MiB", float(1024 ** 2)),
            _lin("GB", "Gigabyte (10⁹ B)", "GB", 1e9),
            _lin("GiB", "Gibibyte (2³⁰ B)", "GiB", float(1024 ** 3)),
            _lin("TB", "Terabyte (10¹² B)", "TB", 1e12),
            _lin("TiB", "Tebibyte (2⁴⁰ B)", "TiB", float(1024 ** 4)),
            _lin("PB", "Petabyte (10¹⁵ B)", "PB", 1e15),
        ],
    ),
    # 9. Data Transfer Rate (base: bit/s)
    CategoryDef(
        key="bitrate",
        name="Data Transfer Rate",
        badge="📡",
        base_unit="bps",
        default_from="Mbps",
        default_to="MBps",
        units=[
            _lin("bps", "Bit per Second", "bps", 1.0),
            _lin("Kbps", "Kilobit per Second", "Kbps", 1e3),
            _lin("Mbps", "Megabit per Second", "Mbps", 1e6),
            _lin("Gbps", "Gigabit per Second", "Gbps", 1e9),
            _lin("Bps", "Byte per Second", "B/s", 8.0),
            _lin("KBps", "Kilobyte per Second", "KB/s", 8e3),
            _lin("MBps", "Megabyte per Second", "MB/s", 8e6),
            _lin("MiBps", "Mebibyte per Second", "MiB/s", 8.0 * (1024 ** 2)),
            _lin("GBps", "Gigabyte per Second", "GB/s", 8e9),
        ],
    ),
    # 10. Energy & Work (base: Joule)
    CategoryDef(
        key="energy",
        name="Energy & Work",
        badge="⚡",
        base_unit="J",
        default_from="kWh",
        default_to="kcal",
        units=[
            _lin("eV", "Electronvolt", "eV", 1.602176634e-19),
            _lin("erg", "Erg", "erg", 1e-7),
            _lin("J", "Joule", "J", 1.0),
            _lin("kJ", "Kilojoule", "kJ", 1e3),
            _lin("MJ", "Megajoule", "MJ", 1e6),
            _lin("cal", "Gram Calorie", "cal", 4.184),
            _lin("kcal", "Kilocalorie (Food Cal)", "kcal", 4184.0),
            _lin("Wh", "Watt-Hour", "Wh", 3600.0),
            _lin("kWh", "Kilowatt-Hour", "kWh", 3_600_000.0),
            _lin("BTU", "British Thermal Unit", "BTU", 1055.05585262),
            _lin("ftlbf", "Foot-Pound Force", "ft·lbf", 1.3558179483314),
        ],
    ),
    # 11. Power (base: Watt)
    CategoryDef(
        key="power",
        name="Power",
        badge="🔋",
        base_unit="W",
        default_from="kW",
        default_to="hp",
        units=[
            _lin("mW", "Milliwatt", "mW", 1e-3),
            _lin("W", "Watt", "W", 1.0),
            _lin("kW", "Kilowatt", "kW", 1e3),
            _lin("MW", "Megawatt", "MW", 1e6),
            _lin("GW", "Gigawatt", "GW", 1e9),
            _lin("hp", "Mechanical Horsepower", "hp", 745.69987158227),
            _lin("hp_m", "Metric Horsepower (PS)", "PS", 735.49875),
            _lin("btuh", "BTU per Hour", "BTU/h", 0.29307107),
        ],
    ),
    # 12. Pressure (base: Pascal)
    CategoryDef(
        key="pressure",
        name="Pressure",
        badge="🧭",
        base_unit="Pa",
        default_from="bar",
        default_to="psi",
        units=[
            _lin("Pa", "Pascal", "Pa", 1.0),
            _lin("hPa", "Hectopascal / Millibar", "hPa", 100.0),
            _lin("kPa", "Kilopascal", "kPa", 1e3),
            _lin("MPa", "Megapascal", "MPa", 1e6),
            _lin("bar", "Bar", "bar", 100_000.0),
            _lin("atm", "Standard Atmosphere", "atm", 101_325.0),
            _lin("mmHg", "Torr / mmHg", "mmHg", 133.322387415),
            _lin("inHg", "Inch of Mercury", "inHg", 3386.389),
            _lin("psi", "Pound per Sq. Inch", "psi", 6894.757293168),
        ],
    ),
    # 13. Force (base: Newton)
    CategoryDef(
        key="force",
        name="Force",
        badge="🏋️",
        base_unit="N",
        default_from="N",
        default_to="lbf",
        units=[
            _lin("uN", "Micronewton", "µN", 1e-6),
            _lin("mN", "Millinewton", "mN", 1e-3),
            _lin("dyn", "Dyne", "dyn", 1e-5),
            _lin("N", "Newton", "N", 1.0),
            _lin("kN", "Kilonewton", "kN", 1e3),
            _lin("MN", "Meganewton", "MN", 1e6),
            _lin("kgf", "Kilogram-Force", "kgf", 9.80665),
            _lin("lbf", "Pound-Force", "lbf", 4.4482216152605),
            _lin("pdl", "Poundal", "pdl", 0.138254954376),
        ],
    ),
    # 14. Angle (base: radian)
    CategoryDef(
        key="angle",
        name="Plane Angle",
        badge="📐",
        base_unit="rad",
        default_from="deg",
        default_to="rad",
        units=[
            _lin("deg", "Degree", "°", math.pi / 180.0),
            _lin("rad", "Radian", "rad", 1.0),
            _lin("grad", "Gradian (Gon)", "grad", math.pi / 200.0),
            _lin("arcmin", "Arcminute", "′", math.pi / (180.0 * 60.0)),
            _lin("arcsec", "Arcsecond", "″", math.pi / (180.0 * 3600.0)),
            _lin("rev", "Revolution / Turn", "rev", math.tau),
        ],
    ),
    # 15. Frequency (base: Hertz)
    CategoryDef(
        key="frequency",
        name="Frequency & RPM",
        badge="〰️",
        base_unit="Hz",
        default_from="Hz",
        default_to="rpm",
        units=[
            _lin("mHz", "Millihertz", "mHz", 1e-3),
            _lin("Hz", "Hertz", "Hz", 1.0),
            _lin("kHz", "Kilohertz", "kHz", 1e3),
            _lin("MHz", "Megahertz", "MHz", 1e6),
            _lin("GHz", "Gigahertz", "GHz", 1e9),
            _lin("THz", "Terahertz", "THz", 1e12),
            _lin("rpm", "Revolutions per Minute", "rpm", 1.0 / 60.0),
        ],
    ),
    # 16. Fuel Economy (base: km/L; exact inverse formula for L/100km)
    CategoryDef(
        key="fuel",
        name="Fuel Economy",
        badge="⛽",
        base_unit="kml",
        default_from="l100",
        default_to="mpg_us",
        units=[
            _lin("kml", "Kilometers per Liter", "km/L", 1.0),
            UnitDef(
                "l100",
                "Liters per 100 km",
                "L/100km",
                lambda v: (100.0 / v) if abs(v) > 1e-15 else 0.0,
                lambda b: (100.0 / b) if abs(b) > 1e-15 else 0.0,
            ),
            _lin("mpg_us", "Miles per US Gallon", "MPG (US)", 1.609344 / 3.785411784),
            _lin("mpg_uk", "Miles per UK Gallon", "MPG (UK)", 1.609344 / 4.54609),
        ],
    ),
]

CATEGORY_MAP: Dict[str, CategoryDef] = {c.key: c for c in CATEGORIES}


def get_unit(cat_key: str, unit_code: str) -> Optional[UnitDef]:
    cat = CATEGORY_MAP.get(cat_key)
    if cat is None:
        return None
    for u in cat.units:
        if u.code == unit_code:
            return u
    return None


def convert_value(cat_key: str, value: float, from_code: str, to_code: str) -> float:
    u_from = get_unit(cat_key, from_code)
    u_to = get_unit(cat_key, to_code)
    if u_from is None or u_to is None:
        raise ValueError(f"Unknown unit '{from_code}' or '{to_code}' in '{cat_key}'")
    if from_code == to_code:
        return value
    base_val = u_from.to_base(value)
    return u_to.from_base(base_val)


def convert_all(cat_key: str, value: float, from_code: str) -> List[Tuple[UnitDef, float]]:
    cat = CATEGORY_MAP[cat_key]
    u_from = get_unit(cat_key, from_code)
    if u_from is None:
        raise ValueError(f"Unknown unit '{from_code}'")
    base_val = u_from.to_base(value)
    return [(u, value if u.code == from_code else u.from_base(base_val)) for u in cat.units]
