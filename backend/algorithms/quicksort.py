"""In-place quicksort, median-of-three pivot (no sorted()/sort_values()).

Used to sort API result rows by an arbitrary column (fare, distance, time)
before returning them to the dashboard.

Complexity:
  time  O(n log n) average, O(n²) worst case
        (median-of-three pivot makes the worst case unlikely on real data,
        e.g. presorted or duplicate-heavy fare columns)
  space O(log n) — recursion stack; sort itself is in-place
"""


def quicksort(items, key=lambda x: x, reverse=False):
    """Sort list in place; also returns it for convenience."""
    _qs(items, 0, len(items) - 1, key)
    if reverse:
        _reverse_in_place(items)
    return items


def _qs(a, lo, hi, key):
    while lo < hi:
        p = _partition(a, lo, hi, key)
        # Recurse on the smaller side first → stack depth stays O(log n)
        if p - lo < hi - p:
            _qs(a, lo, p - 1, key)
            lo = p + 1
        else:
            _qs(a, p + 1, hi, key)
            hi = p - 1


def _partition(a, lo, hi, key):
    _median_of_three(a, lo, hi, key)
    pivot = key(a[hi])
    i = lo - 1
    for j in range(lo, hi):
        if key(a[j]) <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[hi] = a[hi], a[i + 1]
    return i + 1


def _median_of_three(a, lo, hi, key):
    """Place median of a[lo], a[mid], a[hi] at a[hi] as the pivot."""
    mid = (lo + hi) // 2
    if key(a[mid]) < key(a[lo]):
        a[mid], a[lo] = a[lo], a[mid]
    if key(a[hi]) < key(a[lo]):
        a[hi], a[lo] = a[lo], a[hi]
    if key(a[mid]) < key(a[hi]):
        a[mid], a[hi] = a[hi], a[mid]


def _reverse_in_place(a):
    i, j = 0, len(a) - 1
    while i < j:
        a[i], a[j] = a[j], a[i]
        i, j = i + 1, j - 1
