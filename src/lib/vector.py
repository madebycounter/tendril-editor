def distance_to_line(a, b, c):
    try:
        m1 = (b.y - a.y) / (b.x - a.x)
    except ZeroDivisionError:
        m1 = 99999

    try:
        m2 = -1 / m1
    except ZeroDivisionError:
        m2 = 99999

    b1 = a.y - m1 * a.x
    b2 = c.y - m2 * c.x

    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1

    if x < min(a.x, b.x) or x > max(a.x, b.x):
        return min(Vector.Distance(a, c), Vector.Distance(b, c))

    return Vector.Distance((x, y), c)


class Vector:
    AttrMap = {
        "x": 0,
        "y": 1,
        "z": 2,
        "w": 3,
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "width": 0,
        "height": 1,
    }

    @staticmethod
    def Distance(a, b):
        if Vector.IsVector(a) and Vector.IsVector(b):
            return sum([(v2 - v1) ** 2 for v1, v2 in zip(a.values, b.values)]) ** 0.5
        return sum([(v2 - v1) ** 2 for v1, v2 in zip(a, b)]) ** 0.5

    @staticmethod
    def IsVector(v):
        return isinstance(v, Vector)

    @staticmethod
    def IsArrayType(other):
        return isinstance(other, (list, tuple))

    def __init__(self, *values):
        self.values = values

    def __repr__(self):
        return f"v{len(self)}{self.values}"

    def __len__(self):
        return len(self.values)

    def __getitem__(self, idx):
        return self.values[idx]

    def __setitem__(self, idx, value):
        self.values[idx] = value

    def __getattribute__(self, __name: str):
        if __name in Vector.AttrMap:
            return self.values[Vector.AttrMap[__name]]
        else:
            return super().__getattribute__(__name)

    def __setattr__(self, __name: str, value):
        if __name in Vector.AttrMap:
            self.values[Vector.AttrMap[__name]] = value
        else:
            super().__setattr__(__name, value)

    def magnitude(self):
        return sum([v**2 for v in self.values]) ** 0.5

    def operate(self, func, other):
        if Vector.IsVector(other):
            return Vector(*[func(a, b) for a, b in zip(self.values, other.values)])
        elif Vector.IsArrayType(other):
            return Vector(*[func(a, b) for a, b in zip(self.values, other)])
        else:
            return Vector(*[func(a, other) for a in self.values])

    def __add__(self, other):
        return self.operate(lambda a, b: a + b, other)

    def __sub__(self, other):
        return self.operate(lambda a, b: a - b, other)

    def __rsub__(self, other):
        return self.operate(lambda a, b: b - a, other)

    def __mul__(self, other):
        return self.operate(lambda a, b: a * b, other)

    def __truediv__(self, other):
        return self.operate(lambda a, b: a / b, other)

    def __floordiv__(self, other):
        return self.operate(lambda a, b: a // b, other)

    def __mod__(self, other):
        return self.operate(lambda a, b: a % b, other)

    def __pow__(self, other):
        return self.operate(lambda a, b: a**b, other)

    def __neg__(self):
        return Vector(*[-a for a in self.values])

    def __pos__(self):
        return Vector(*[+a for a in self.values])

    def __abs__(self):
        return Vector(*[abs(a) for a in self.values])

    def __invert__(self):
        return Vector(*[~a for a in self.values])
