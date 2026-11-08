# PRISM CALC — Scientific Calculator, Measuring Converter & Suite

A modern, zero-dependency **Python Tkinter** desktop suite combining a full **Scientific Calculator**, a **16-Category / 150+ Unit Measuring Converter**, a **Programmer Base & Bitwise Inspector**, an **Interactive 2D Function Grapher**, and **Engineering & Everyday Math Tools**.

Built with custom `tk.Canvas` rounded widgets so every button, card, dropdown, and hover animation renders with crisp, vibrant colors across **macOS** (immune to Aqua `tk.Button` background overrides), **Windows**, and **Linux**.

---

## Quick Start

```bash
cd ~/Downloads/tkinter_calconv_proj
chmod +x run.sh
./run.sh
```

Or run directly with Python 3:

```bash
python3 main.py
```

Run the built-in non-GUI verification suite:

```bash
python3 main.py --self-test
```

> **macOS Homebrew Note:** If your Homebrew `python3` does not yet have `python-tk`, `./run.sh` automatically detects a Tkinter-capable Python on your Mac or installs `python-tk` via Homebrew.

---

## What's Inside

1. **Scientific Calculator (`Cmd/Ctrl + 1`)**
   - Live instant expression preview as you type + scrollable **Calculation Tape** (click any history item to reuse its expression or value).
   - `DEG` / `RAD` / `GRAD` angle modes with exact clean-angle trig snapping (`sin(180°) = 0`, `cos(90°) = 0`, `tan(45°) = 1`).
   - `2nd` shift pad (`sin ↔ asin`, `cos ↔ acos`, `tan ↔ atan`, `sinh ↔ asinh`, `ln ↔ eˣ`, `log ↔ 10ˣ`, `x² ↔ x³`, `√x ↔ ∛x`, `xʸ ↔ ʸ√x`, `nCr ↔ gcd`, `nPr ↔ lcm`).
   - **Constants Popover**: 16 physical & mathematical constants (`π`, `e`, `τ`, `φ`, `c`, `g`, `G`, `h`, `ℏ`, `Nₐ`, `k_B`, `R`, `q_e`, `m_e`, `m_p`, `ε₀`).
   - Full Memory bank (`MC`, `MR`, `M+`, `M-`, `MS`), `F-E` scientific notation toggle, `Ans`, and one-click `→ Converter` handoff.

2. **Measuring & Unit Converter (`Cmd/Ctrl + 2`)**
   - **16 Measurement Categories & 150+ Units**:
     - Length & Distance, Mass & Weight, Temperature (`°C`, `°F`, `K`, `°R`, `°Ré`), Area, Volume & Capacity, Speed & Velocity, Time & Duration, Digital Data Storage (`KB` vs `KiB`, `GB` vs `GiB`, etc.), Data Transfer Rate, Energy & Work, Power, Pressure, Force, Plane Angle, Frequency & RPM, and Fuel Economy (`km/L`, `L/100km`, `MPG US`, `MPG UK`).
   - Supports inline expressions right in the input box (e.g., `5 + 3/8` or `2 * pi`), `⇅ Swap Units`, searchable unit popovers, `→ Scientific` handoff, and a live **All Equivalent Units** comparison table.

3. **Programmer Calculator (`Cmd/Ctrl + 3`)**
   - Live simultaneous `HEX`, `DEC`, `OCT`, and `BIN` readouts across `64-bit QWORD`, `32-bit DWORD`, `16-bit WORD`, and `8-bit BYTE` (Signed 2's complement & Unsigned).
   - Interactive **64-bit Clickable Bit Inspector** (`0 ↔ 1`) plus `AND`, `OR`, `XOR`, `NOT`, `<<`, `>>`, `RoL`, `RoR`, and `MOD`.

4. **2D Function Grapher (`Cmd/Ctrl + 4`)**
   - Plot up to 3 simultaneous functions `f(x)`, `g(x)`, `h(x)` with mouse drag-to-pan, scroll-to-zoom, asymptote detection, live hover coordinate crosshair, numerical derivative `f'(x₀)`, and shaded Simpson's-rule definite integral `∫ f(x) dx`.

5. **Engineering & Everyday Math Tools (`Cmd/Ctrl + 5`)**
   - **Polynomial Roots**: Quadratic (`ax² + bx + c = 0`) & Cubic (`ax³ + bx² + cx + d = 0`) real and complex root solvers.
   - **Linear Systems**: `2×2` and `3×3` matrix `Ax = b` solver.
   - **Statistics Lab**: Count, Sum, Mean, Median, Mode, Sample & Population Std Dev, Variance, Quartiles (`Q₁`, `Q₃`, `IQR`), and Geometric/Harmonic Mean.
   - **Finance**: Loan EMI & Amortization + Compound Investment Growth.
   - **Date & BMI**: Exact calendar span + business days calculator & WHO BMI calculator.

6. **3 Live Color Themes**
   - Toggle anytime in the top-right corner between **Midnight Obsidian**, **Aurora Cyber**, and **Solar Ivory**.
