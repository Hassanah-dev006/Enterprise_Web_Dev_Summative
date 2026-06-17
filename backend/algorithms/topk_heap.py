class MinHeap:
    """Array-backed binary min-heap ordered by `key(item)`."""

    def __init__(self, key=lambda x: x):
        self._a = []
        self._key = key

    def __len__(self):
        return len(self._a)

    def peek(self):
        return self._a[0]

    def push(self, item):
        self._a.append(item)
        self._sift_up(len(self._a) - 1)

    def replace_root(self, item):
        self._a[0] = item
        self._sift_down(0)

    def pop(self):
        root = self._a[0]
        last = self._a.pop()
        if self._a:
            self._a[0] = last
            self._sift_down(0)
        return root

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self._key(self._a[i]) < self._key(self._a[parent]):
                self._a[i], self._a[parent] = self._a[parent], self._a[i]
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self._a)
        while True:
            left, right, smallest = 2 * i + 1, 2 * i + 2, i
            if left < n and self._key(self._a[left]) < self._key(self._a[smallest]):
                smallest = left
            if right < n and self._key(self._a[right]) < self._key(self._a[smallest]):
                smallest = right
            if smallest == i:
                return
            self._a[i], self._a[smallest] = self._a[smallest], self._a[i]
            i = smallest


def top_k(items, k, key=lambda x: x):
    """Return the k largest items, descending. O(n log k) time, O(k) space."""
    if k <= 0:
        return []
    heap = MinHeap(key=key)
    for item in items:
        if len(heap) < k:
            heap.push(item)
        elif key(item) > key(heap.peek()):
            heap.replace_root(item)
    # Drain ascending, then reverse → descending
    out = []
    while len(heap):
        out.append(heap.pop())
    out.reverse()
    return out
