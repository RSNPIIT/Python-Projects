"""Engineering & Everyday Tools View: Equations, Linear Systems, Statistics, Finance & Date/BMI."""

from __future__ import annotations

import datetime as dt
import tkinter as tk
from typing import Dict, List, Tuple

from ..solvers import (
    compute_bmi,
    compute_date_diff,
    compute_loan_and_compound,
    compute_statistics,
    solve_cubic,
    solve_linear_system,
    solve_quadratic,
)
from ..theme import FontSet
from ..widgets import RoundedButton, RoundedCard, SegmentedBar, StyledEntry


class ToolsView(tk.Frame):
    """Multi-tool engineering & everyday math suite."""

    def __init__(self, parent: tk.Widget, *, fonts: FontSet, palette: Dict[str, str]) -> None:
        super().__init__(parent, bg=palette["bg"], bd=0, highlightthickness=0)
        self.fonts = fonts
        self.palette = palette
        self.active_tool = "equations"

        self._build_ui()
        self._switch_tool("equations")

    def _build_ui(self) -> None:
        p = self.palette
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.sub_bar = SegmentedBar(
            self,
            [
                ("equations", "Polynomial Roots"),
                ("linear", "2×2 & 3×3 Matrix"),
                ("stats", "Statistics Lab"),
                ("finance", "Loan & Compound"),
                ("date_bmi", "Date & BMI"),
            ],
            selected="equations",
            on_change=self._switch_tool,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["bg"],
            height=36,
            font_size=11,
        )
        self.sub_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.stage_card = RoundedCard(
            self,
            palette=p,
            parent_bg=p["bg"],
            fill_key="surface",
            border_key="card_border",
            radius=16,
            pad_x=20,
            pad_y=16,
        )
        self.stage_card.grid(row=1, column=0, sticky="nsew")

    def _clear_stage(self) -> tk.Frame:
        body = self.stage_card.body
        for child in body.winfo_children():
            child.destroy()
        body.configure(bg=self.palette["surface"])
        return body

    def _render_kv_table(self, parent: tk.Widget, rows: List[Tuple[str, str]]) -> None:
        p = self.palette
        for child in parent.winfo_children():
            child.destroy()
        for k, v in rows:
            rframe = tk.Frame(parent, bg=p["display_bg"], padx=14, pady=8)
            rframe.pack(fill="x", pady=3)
            tk.Label(
                rframe,
                text=k,
                anchor="w",
                bg=p["display_bg"],
                fg=p["text_sub"],
                font=self.fonts.ui(11),
            ).pack(side="left")
            tk.Label(
                rframe,
                text=v,
                anchor="e",
                bg=p["display_bg"],
                fg=p["secondary"],
                font=self.fonts.mono(12, "bold"),
            ).pack(side="right")

    def _switch_tool(self, key: str) -> None:
        self.active_tool = key
        if key == "equations":
            self._build_equations()
        elif key == "linear":
            self._build_linear()
        elif key == "stats":
            self._build_stats()
        elif key == "finance":
            self._build_finance()
        else:
            self._build_date_bmi()

    # ------------------------------------------------------------------
    # 1. Polynomial Equations (Quadratic & Cubic)
    # ------------------------------------------------------------------
    def _build_equations(self) -> None:
        p = self.palette
        b = self._clear_stage()
        b.grid_columnconfigure(0, weight=1, uniform="eqc")
        b.grid_columnconfigure(1, weight=1, uniform="eqc")
        b.grid_rowconfigure(0, weight=1)

        # Left: Quadratic
        qframe = tk.Frame(b, bg=p["surface"], padx=8)
        qframe.grid(row=0, column=0, sticky="nsew")
        tk.Label(
            qframe,
            text="QUADRATIC SOLVER  ·  a·x² + b·x + c = 0",
            anchor="w",
            bg=p["surface"],
            fg=p["accent"],
            font=self.fonts.ui(12, "bold"),
        ).pack(fill="x", pady=(0, 10))

        q_inputs = tk.Frame(qframe, bg=p["surface"])
        q_inputs.pack(fill="x", pady=(0, 10))
        q_entries: List[StyledEntry] = []
        for idx, (lbl, dflt) in enumerate((("a =", "1"), ("b =", "-5"), ("c =", "6"))):
            q_inputs.grid_columnconfigure(idx * 2 + 1, weight=1)
            tk.Label(q_inputs, text=lbl, bg=p["surface"], fg=p["text_sub"], font=self.fonts.mono(11)).grid(
                row=0, column=idx * 2, padx=(6 if idx else 0, 4)
            )
            ent = StyledEntry(q_inputs, fonts=self.fonts, palette=p, parent_bg=p["surface"], initial=dflt, height=38)
            ent.grid(row=0, column=idx * 2 + 1, sticky="ew")
            q_entries.append(ent)

        q_out = tk.Frame(qframe, bg=p["surface"])

        def _run_quad() -> None:
            try:
                vals = [float(e.get().strip()) for e in q_entries]
                self._render_kv_table(q_out, solve_quadratic(*vals))
            except ValueError:
                self._render_kv_table(q_out, [("Error", "Enter valid numeric coefficients")])

        RoundedButton(
            qframe,
            "Solve Quadratic",
            command=_run_quad,
            kind="eq",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            height=38,
        ).pack(fill="x", pady=(0, 12))
        q_out.pack(fill="both", expand=True)
        _run_quad()

        # Right: Cubic
        cframe = tk.Frame(b, bg=p["surface"], padx=8)
        cframe.grid(row=0, column=1, sticky="nsew")
        tk.Label(
            cframe,
            text="CUBIC SOLVER  ·  a·x³ + b·x² + c·x + d = 0",
            anchor="w",
            bg=p["surface"],
            fg=p["secondary"],
            font=self.fonts.ui(12, "bold"),
        ).pack(fill="x", pady=(0, 10))

        c_inputs = tk.Frame(cframe, bg=p["surface"])
        c_inputs.pack(fill="x", pady=(0, 10))
        c_entries: List[StyledEntry] = []
        for idx, (lbl, dflt) in enumerate((("a=", "1"), ("b=", "-6"), ("c=", "11"), ("d=", "-6"))):
            c_inputs.grid_columnconfigure(idx * 2 + 1, weight=1)
            tk.Label(c_inputs, text=lbl, bg=p["surface"], fg=p["text_sub"], font=self.fonts.mono(10)).grid(
                row=0, column=idx * 2, padx=(5 if idx else 0, 3)
            )
            ent = StyledEntry(c_inputs, fonts=self.fonts, palette=p, parent_bg=p["surface"], initial=dflt, height=38, font_size=12)
            ent.grid(row=0, column=idx * 2 + 1, sticky="ew")
            c_entries.append(ent)

        c_out = tk.Frame(cframe, bg=p["surface"])

        def _run_cubic() -> None:
            try:
                vals = [float(e.get().strip()) for e in c_entries]
                self._render_kv_table(c_out, solve_cubic(*vals))
            except ValueError:
                self._render_kv_table(c_out, [("Error", "Enter valid numeric coefficients")])

        RoundedButton(
            cframe,
            "Solve Cubic",
            command=_run_cubic,
            kind="op",
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            height=38,
        ).pack(fill="x", pady=(0, 12))
        c_out.pack(fill="both", expand=True)
        _run_cubic()

    # ------------------------------------------------------------------
    # 2. 2×2 & 3×3 Linear System Solver
    # ------------------------------------------------------------------
    def _build_linear(self) -> None:
        p = self.palette
        b = self._clear_stage()
        b.grid_columnconfigure(0, weight=1, uniform="linc")
        b.grid_columnconfigure(1, weight=1, uniform="linc")
        b.grid_rowconfigure(0, weight=1)

        # 2x2
        f2 = tk.Frame(b, bg=p["surface"], padx=8)
        f2.grid(row=0, column=0, sticky="nsew")
        tk.Label(f2, text="2×2 LINEAR SYSTEM  (a·x + b·y = c)", anchor="w", bg=p["surface"], fg=p["accent"], font=self.fonts.ui(12, "bold")).pack(fill="x", pady=(0, 10))
        grid2 = tk.Frame(f2, bg=p["surface"])
        grid2.pack(fill="x", pady=(0, 10))
        defaults2 = [["2", "3", "13"], ["5", "-1", "7"]]
        ents2: List[List[StyledEntry]] = []
        for r in range(2):
            row_e = []
            for c_idx in range(3):
                grid2.grid_columnconfigure(c_idx * 2, weight=1)
                e = StyledEntry(grid2, fonts=self.fonts, palette=p, parent_bg=p["surface"], initial=defaults2[r][c_idx], height=38, justify="center")
                e.grid(row=r, column=c_idx * 2, sticky="ew", pady=3)
                row_e.append(e)
                sep = "x +" if c_idx == 0 else ("y =" if c_idx == 1 else "")
                if sep:
                    tk.Label(grid2, text=sep, bg=p["surface"], fg=p["text_sub"], font=self.fonts.mono(11)).grid(row=r, column=c_idx * 2 + 1, padx=6)
            ents2.append(row_e)

        out2 = tk.Frame(f2, bg=p["surface"])

        def _solve2() -> None:
            try:
                mat = [[float(ents2[r][0].get()), float(ents2[r][1].get())] for r in range(2)]
                rhs = [float(ents2[r][2].get()) for r in range(2)]
                self._render_kv_table(out2, solve_linear_system(mat, rhs))
            except ValueError:
                self._render_kv_table(out2, [("Error", "Enter valid numbers")])

        RoundedButton(f2, "Solve 2×2 System", command=_solve2, kind="eq", fonts=self.fonts, palette=p, parent_bg=p["surface"], height=38).pack(fill="x", pady=(4, 12))
        out2.pack(fill="both", expand=True)
        _solve2()

        # 3x3
        f3 = tk.Frame(b, bg=p["surface"], padx=8)
        f3.grid(row=0, column=1, sticky="nsew")
        tk.Label(f3, text="3×3 LINEAR SYSTEM  (a·x + b·y + c·z = d)", anchor="w", bg=p["surface"], fg=p["secondary"], font=self.fonts.ui(12, "bold")).pack(fill="x", pady=(0, 10))
        grid3 = tk.Frame(f3, bg=p["surface"])
        grid3.pack(fill="x", pady=(0, 10))
        defaults3 = [["1", "1", "1", "6"], ["2", "-1", "1", "3"], ["1", "2", "-1", "2"]]
        ents3: List[List[StyledEntry]] = []
        for r in range(3):
            row_e = []
            for c_idx in range(4):
                grid3.grid_columnconfigure(c_idx * 2, weight=1)
                e = StyledEntry(grid3, fonts=self.fonts, palette=p, parent_bg=p["surface"], initial=defaults3[r][c_idx], height=36, font_size=12, justify="center")
                e.grid(row=r, column=c_idx * 2, sticky="ew", pady=2)
                row_e.append(e)
                sep = "x+" if c_idx == 0 else ("y+" if c_idx == 1 else ("z=" if c_idx == 2 else ""))
                if sep:
                    tk.Label(grid3, text=sep, bg=p["surface"], fg=p["text_sub"], font=self.fonts.mono(10)).grid(row=r, column=c_idx * 2 + 1, padx=4)
            ents3.append(row_e)

        out3 = tk.Frame(f3, bg=p["surface"])

        def _solve3() -> None:
            try:
                mat = [[float(ents3[r][c].get()) for c in range(3)] for r in range(3)]
                rhs = [float(ents3[r][3].get()) for r in range(3)]
                self._render_kv_table(out3, solve_linear_system(mat, rhs))
            except ValueError:
                self._render_kv_table(out3, [("Error", "Enter valid numbers")])

        RoundedButton(f3, "Solve 3×3 System", command=_solve3, kind="op", fonts=self.fonts, palette=p, parent_bg=p["surface"], height=38).pack(fill="x", pady=(4, 12))
        out3.pack(fill="both", expand=True)
        _solve3()

    # ------------------------------------------------------------------
    # 3. Statistics Lab
    # ------------------------------------------------------------------
    def _build_stats(self) -> None:
        p = self.palette
        b = self._clear_stage()
        tk.Label(
            b,
            text="DESCRIPTIVE STATISTICS LAB  ·  ENTER COMMA OR SPACE SEPARATED DATASET",
            anchor="w",
            bg=p["surface"],
            fg=p["accent"],
            font=self.fonts.ui(12, "bold"),
        ).pack(fill="x", pady=(0, 8))

        data_entry = StyledEntry(
            b,
            fonts=self.fonts,
            palette=p,
            parent_bg=p["surface"],
            initial="12, 15, 18, 22, 22, 25, 29, 34, 41, 45",
            font_size=13,
            height=44,
        )
        data_entry.pack(fill="x", pady=(0, 10))

        out_grid = tk.Frame(b, bg=p["surface"])

        def _run_stats() -> None:
            for ch in out_grid.winfo_children():
                ch.destroy()
            out_grid.grid_columnconfigure(0, weight=1, uniform="stc")
            out_grid.grid_columnconfigure(1, weight=1, uniform="stc")
            try:
                rows = compute_statistics(data_entry.get())
            except Exception as exc:
                rows = [("Input Error", str(exc))]

            for idx, (k, v) in enumerate(rows):
                r, c = divmod(idx, 2)
                cell = tk.Frame(out_grid, bg=p["display_bg"], padx=12, pady=8)
                cell.grid(row=r, column=c, sticky="ew", padx=4, pady=3)
                tk.Label(cell, text=k, bg=p["display_bg"], fg=p["text_sub"], font=self.fonts.ui(10)).pack(side="left")
                tk.Label(cell, text=v, bg=p["display_bg"], fg=p["secondary"], font=self.fonts.mono(11, "bold")).pack(side="right")

        data_entry.var.trace_add("write", lambda *_: _run_stats())
        out_grid.pack(fill="both", expand=True, pady=(4, 0))
        _run_stats()

    # ------------------------------------------------------------------
    # 4. Finance: Loan EMI & Compound Growth
    # ------------------------------------------------------------------
    def _build_finance(self) -> None:
        p = self.palette
        b = self._clear_stage()

        in_row = tk.Frame(b, bg=p["surface"])
        in_row.pack(fill="x", pady=(0, 14))
        fields = [
            ("Principal Amount", "100000"),
            ("Annual Rate (%)", "7.5"),
            ("Term (Years)", "10"),
            ("Compounds / Yr", "12"),
        ]
        entries: List[StyledEntry] = []
        for idx, (lbl, dflt) in enumerate(fields):
            in_row.grid_columnconfigure(idx, weight=1)
            col_f = tk.Frame(in_row, bg=p["surface"], padx=5)
            col_f.grid(row=0, column=idx, sticky="ew")
            tk.Label(col_f, text=lbl, anchor="w", bg=p["surface"], fg=p["text_sub"], font=self.fonts.ui(10, "bold")).pack(fill="x", pady=(0, 4))
            e = StyledEntry(col_f, fonts=self.fonts, palette=p, parent_bg=p["surface"], initial=dflt, height=40)
            e.pack(fill="x")
            entries.append(e)

        cols = tk.Frame(b, bg=p["surface"])
        cols.pack(fill="both", expand=True)
        cols.grid_columnconfigure(0, weight=1, uniform="finc")
        cols.grid_columnconfigure(1, weight=1, uniform="finc")

        left_box = tk.Frame(cols, bg=p["surface"], padx=6)
        left_box.grid(row=0, column=0, sticky="nsew")
        tk.Label(left_box, text="LOAN AMORTIZATION (EMI)", anchor="w", bg=p["surface"], fg=p["accent"], font=self.fonts.ui(11, "bold")).pack(fill="x", pady=(0, 8))
        loan_out = tk.Frame(left_box, bg=p["surface"])
        loan_out.pack(fill="both", expand=True)

        right_box = tk.Frame(cols, bg=p["surface"], padx=6)
        right_box.grid(row=0, column=1, sticky="nsew")
        tk.Label(right_box, text="COMPOUND INVESTMENT GROWTH", anchor="w", bg=p["surface"], fg=p["secondary"], font=self.fonts.ui(11, "bold")).pack(fill="x", pady=(0, 8))
        comp_out = tk.Frame(right_box, bg=p["surface"])
        comp_out.pack(fill="both", expand=True)

        def _calc_fin() -> None:
            try:
                pr = float(entries[0].get().replace(",", ""))
                rt = float(entries[1].get())
                yr = float(entries[2].get())
                cp = int(float(entries[3].get()))
                res = compute_loan_and_compound(pr, rt, yr, cp)
                self._render_kv_table(loan_out, res["loan"])
                self._render_kv_table(comp_out, res["compound"])
            except Exception as exc:
                self._render_kv_table(loan_out, [("Check Inputs", str(exc))])
                self._render_kv_table(comp_out, [])

        for e in entries:
            e.var.trace_add("write", lambda *_: _calc_fin())
        _calc_fin()

    # ------------------------------------------------------------------
    # 5. Date Span & BMI Calculator
    # ------------------------------------------------------------------
    def _build_date_bmi(self) -> None:
        p = self.palette
        b = self._clear_stage()
        b.grid_columnconfigure(0, weight=1, uniform="dbc")
        b.grid_columnconfigure(1, weight=1, uniform="dbc")
        b.grid_rowconfigure(0, weight=1)

        # Left: Date Span
        dframe = tk.Frame(b, bg=p["surface"], padx=8)
        dframe.grid(row=0, column=0, sticky="nsew")
        tk.Label(dframe, text="DATE & WORKDAY SPAN  (YYYY-MM-DD)", anchor="w", bg=p["surface"], fg=p["accent"], font=self.fonts.ui(12, "bold")).pack(fill="x", pady=(0, 10))

        today = dt.date.today()
        jan1 = dt.date(today.year, 1, 1)
        d_in = tk.Frame(dframe, bg=p["surface"])
        d_in.pack(fill="x", pady=(0, 10))
        d_in.grid_columnconfigure(0, weight=1)
        d_in.grid_columnconfigure(1, weight=1)

        d1_e = StyledEntry(d_in, fonts=self.fonts, palette=p, parent_bg=p["surface"], initial=jan1.isoformat(), height=40)
        d1_e.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        d2_e = StyledEntry(d_in, fonts=self.fonts, palette=p, parent_bg=p["surface"], initial=today.isoformat(), height=40)
        d2_e.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        d_out = tk.Frame(dframe, bg=p["surface"])
        d_out.pack(fill="both", expand=True)

        def _calc_dates() -> None:
            try:
                self._render_kv_table(d_out, compute_date_diff(d1_e.get(), d2_e.get()))
            except Exception:
                self._render_kv_table(d_out, [("Format", "Enter dates as YYYY-MM-DD")])

        d1_e.var.trace_add("write", lambda *_: _calc_dates())
        d2_e.var.trace_add("write", lambda *_: _calc_dates())
        _calc_dates()

        # Right: BMI & Body Metrics
        mframe = tk.Frame(b, bg=p["surface"], padx=8)
        mframe.grid(row=0, column=1, sticky="nsew")
        tk.Label(mframe, text="BMI & HEALTHY WEIGHT CALCULATOR", anchor="w", bg=p["surface"], fg=p["secondary"], font=self.fonts.ui(12, "bold")).pack(fill="x", pady=(0, 10))

        m_in = tk.Frame(mframe, bg=p["surface"])
        m_in.pack(fill="x", pady=(0, 10))
        m_in.grid_columnconfigure(0, weight=1)
        m_in.grid_columnconfigure(1, weight=1)

        tk.Label(m_in, text="Weight (kg)", anchor="w", bg=p["surface"], fg=p["text_sub"], font=self.fonts.ui(10)).grid(row=0, column=0, sticky="w")
        tk.Label(m_in, text="Height (cm)", anchor="w", bg=p["surface"], fg=p["text_sub"], font=self.fonts.ui(10)).grid(row=0, column=1, sticky="w", padx=(8, 0))

        w_e = StyledEntry(m_in, fonts=self.fonts, palette=p, parent_bg=p["surface"], initial="70", height=40)
        w_e.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        h_e = StyledEntry(m_in, fonts=self.fonts, palette=p, parent_bg=p["surface"], initial="175", height=40)
        h_e.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        m_out = tk.Frame(mframe, bg=p["surface"])
        m_out.pack(fill="both", expand=True)

        def _calc_bmi() -> None:
            try:
                self._render_kv_table(m_out, compute_bmi(float(w_e.get()), float(h_e.get())))
            except Exception:
                self._render_kv_table(m_out, [("Input", "Enter positive weight (kg) & height (cm)")])

        w_e.var.trace_add("write", lambda *_: _calc_bmi())
        h_e.var.trace_add("write", lambda *_: _calc_bmi())
        _calc_bmi()

    def apply_theme(self, palette: Dict[str, str]) -> None:
        self.palette = palette
        p = palette
        self.configure(bg=p["bg"])
        self.sub_bar.apply_theme(p, p["bg"])
        self.stage_card.apply_theme(p, p["bg"])
        self._switch_tool(self.active_tool)
