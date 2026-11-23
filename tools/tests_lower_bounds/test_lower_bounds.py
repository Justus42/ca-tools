import csv
import unittest
from fractions import Fraction
from functools import lru_cache
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOUNDS_CSV = ROOT / "table" / "lower_bounds.csv"
SEEDS_CSV = ROOT / "table" / "lower_bound_seeds.csv"
REFERENCES_CSV = ROOT / "table" / "references.csv"


def load_rows():
    with open(BOUNDS_CSV, newline="") as handle:
        rows = []
        for raw in csv.DictReader(handle):
            row = dict(raw)
            for key in ("t", "v", "k_min", "k_max", "bound"):
                row[key] = int(row[key])
            rows.append(row)
        return rows


def load_seeds():
    seeds = {}
    with open(SEEDS_CSV, newline="") as handle:
        for raw in csv.DictReader(handle):
            key = (int(raw["t"]), int(raw["v"]))
            seeds.setdefault(key, []).append((int(raw["k"]), int(raw["bound"])))
    return seeds


SEEDS = load_seeds()


def ceil_div(a, b):
    return -(-a // b)


def rule_r0(t, k, v):
    return v ** t


def rule_r2(t, k, v):
    if t < 3:
        return None
    return v * floor_value(t - 1, k - 1, v)


@lru_cache(maxsize=None)
def rule_r3(t, k, v):
    if t != 2 or v != 2:
        return None
    n = 2
    while comb(n - 1, ceil_div(n, 2)) < k:
        n += 1
    return n


def rule_r5(t, k, v):
    best = None
    for seed_k, seed_bound in SEEDS.get((t, v), []):
        if seed_k <= k and (best is None or seed_bound > best):
            best = seed_bound
    return best


def r6_table():
    table = []
    for m in range(7, 60):
        half = m // 2
        c = comb(m - 1, half - 1)
        if m % 2 == 1:
            lo = c + m - 3 * half
            value = 2 * m + 1
        else:
            lo = c - half
            value = 2 * m + 2
        table.append((lo + 2, value))
    return table


R6_TABLE = r6_table()


def rule_r6(t, k, v):
    if t != 3 or v != 2:
        return None
    best = None
    for start, value in R6_TABLE:
        if k >= start and (best is None or value > best):
            best = value
    return best


@lru_cache(maxsize=None)
def rule_r7(t, k, v):
    if v != 2 or t < 3:
        return None
    u = 2 ** (t - 1)
    target = comb(k, t - 2)
    n = u
    while True:
        q = n // u
        denominator = 2 ** (t - 3) * comb(n // 2 ** (t - 2), q + 1)
        if denominator != 0 and Fraction(comb(n, q + 1), denominator) >= target:
            break
        n += u
    if n == u:
        return None
    return n - u + 1


@lru_cache(maxsize=None)
def rule_r8(t, k, v):
    if v != 2 or t < 3:
        return None
    target = comb(k, t - 1)
    n = 2 ** t
    while sum(comb(n, j) for j in range(n // 2 ** (t - 1) + 1)) < target:
        n += 1
    return n


def rule_r9(t, k, v):
    if t == 2 and v >= 3 and k >= v + 2:
        return v * v + 2
    return None


@lru_cache(maxsize=None)
def rule_r10(t, k, v):
    if t != 2 or v < 3:
        return None
    n = v * v
    while comb(2 * n // v, n // v) < 2 * k:
        n += 1
    return n


def rule_r12(t, k, v):
    if t == 2 and v >= 4 and k >= v + 2:
        return v * v + 3
    return None


def rule_r13(t, k, v):
    if t < 3:
        return None
    if v % 2 == 1 and t < v and k >= v + t - 1:
        return v ** t + 1
    if v % 2 == 0 and t < v and k >= v + t:
        return v ** t + 1
    if t >= v and k >= t + 2:
        return v ** t + 1
    return None


def rule_r14(t, k, v):
    if t < 3:
        return None
    best = None
    if t == 3 and v % 4 == 2 and v >= 6 and k >= v + 1:
        best = v ** 3 + 1
    if v % 2 == 0 and v % 36 != 0 and 4 <= t < v and k >= v + t - 2:
        best = max(best or 0, v ** t + 1)
    if (t, v) == (4, 5) and k >= 7:
        best = max(best or 0, 626)
    return best


def rule_r15(t, k, v):
    if t != 3 or v % 2 == 0 or k < v + 2:
        return None
    if v == 3:
        c = 6
    elif v == 5:
        c = 10
    elif v in (7, 9):
        c = 11
    else:
        c = 12
    return v ** 3 + c


@lru_cache(maxsize=None)
def rule_r16(t, k, v):
    if t != 2 or v < 3:
        return None
    n = v
    while True:
        q = n // v
        d = 1 if n % v == v - 1 else 0
        if comb(2 * q + d, q) >= 2 * k:
            return n
        n += 1


def r17_f(b, v):
    q = b // v
    if q < v - 2:
        return 0
    return comb(b, q - (v - 2)) // (v * comb(q, v - 2))


@lru_cache(maxsize=None)
def rule_r17(t, k, v):
    if t != 2 or v < 3:
        return None
    s = v
    while k > r17_f(s * v, v):
        s += 1
    return s + v * (v - 1)


RULES = {
    "R0": rule_r0,
    "R2": rule_r2,
    "R3": rule_r3,
    "R5": rule_r5,
    "R6": rule_r6,
    "R7": rule_r7,
    "R8": rule_r8,
    "R9": rule_r9,
    "R10": rule_r10,
    "R12": rule_r12,
    "R13": rule_r13,
    "R14": rule_r14,
    "R15": rule_r15,
    "R16": rule_r16,
    "R17": rule_r17,
}


@lru_cache(maxsize=None)
def floor_value(t, k, v):
    if t == 2 and v == 2:
        return rule_r3(t, k, v)
    best = 0
    for rule in RULES.values():
        value = rule(t, k, v)
        if value is not None and value > best:
            best = value
    return best


ROWS = load_rows()


def label(row):
    return "t={t} v={v} k={k_min}..{k_max} bound={bound} rule={rule}".format(**row)


class FloorMatchesRows(unittest.TestCase):
    def test_file_not_empty(self):
        self.assertTrue(ROWS)

    def test_floor_at_endpoints(self):
        failures = []
        for row in ROWS:
            for k in (row["k_min"], row["k_max"]):
                got = floor_value(row["t"], k, row["v"])
                if got != row["bound"]:
                    failures.append("{} : floor at k={} is {}".format(label(row), k, got))
        self.assertEqual(failures, [], "\n".join(failures))

    def test_named_rule_attains_bound(self):
        failures = []
        for row in ROWS:
            rule = RULES.get(row["rule"])
            if rule is None:
                failures.append("{} : unknown rule".format(label(row)))
                continue
            got = rule(row["t"], row["k_min"], row["v"])
            if got != row["bound"]:
                failures.append("{} : named rule gives {}".format(label(row), got))
        self.assertEqual(failures, [], "\n".join(failures))


class RowStructure(unittest.TestCase):
    def test_no_overlap_and_monotone(self):
        groups = {}
        for row in ROWS:
            self.assertLessEqual(row["k_min"], row["k_max"], label(row))
            groups.setdefault((row["t"], row["v"]), []).append(row)
        failures = []
        for key, group in groups.items():
            group.sort(key=lambda r: r["k_min"])
            for prev, cur in zip(group, group[1:]):
                if cur["k_min"] <= prev["k_max"]:
                    failures.append("overlap: {} and {}".format(label(prev), label(cur)))
                if cur["bound"] < prev["bound"]:
                    failures.append("decrease: {} then {}".format(label(prev), label(cur)))
        self.assertEqual(failures, [], "\n".join(failures))


class References(unittest.TestCase):
    def test_reference_ids_known(self):
        self.assertTrue(REFERENCES_CSV.exists(), "missing {}".format(REFERENCES_CSV))
        with open(REFERENCES_CSV, newline="") as handle:
            reader = csv.DictReader(handle)
            column = "id" if "id" in reader.fieldnames else reader.fieldnames[0]
            known = {raw[column].strip() for raw in reader}
        missing = set()
        for row in ROWS:
            for ref in row["reference"].split(";"):
                ref = ref.strip()
                if ref and ref not in known:
                    missing.add(ref)
        self.assertEqual(sorted(missing), [], "unknown reference ids: {}".format(sorted(missing)))


if __name__ == "__main__":
    unittest.main()
