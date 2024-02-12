from math import floor


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


def normalize(veins):
    flat = [p for v in veins for p in v]

    orig = veins[0][0]

    tl = (
        min(flat, key=lambda x: x[0])[0],
        min(flat, key=lambda x: x[1])[1],
    )

    br = (
        max(flat, key=lambda x: x[0])[0],
        max(flat, key=lambda x: x[1])[1],
    )

    size = (
        br[0] - tl[0],
        br[1] - tl[1],
    )

    sf = 1 / size[0]

    return [
        [
            (
                (p[0] - orig[0]) * sf,
                (p[1] - orig[1]) * sf,
            )
            for p in v
        ]
        for v in veins
    ]


def line_length(points):
    length = 0
    for i in range(len(points) - 1):
        length += Vector.Distance(points[i], points[i + 1])

    return length


def step_to(points, pct):
    dist = line_length(points) * pct

    current = 0
    for i in range(len(points) - 1):
        length = Vector.Distance(points[i], points[i + 1])

        if current + length > dist:
            return points[i] + (points[i + 1] - points[i]) * (dist - current) / length

        current += length

    return points[-1]


def step_to_time(points, pct):
    posn = (len(points) - 1) * pct
    idx = floor(posn)
    extra = posn - idx

    return points[idx] + (points[idx + 1] - points[idx]) * extra


def piecewise(points, modifier=lambda x: 1, N=120):
    # calculate length lines formed by array of points
    step = line_length(points) / N

    # calculate points along lines
    new_points = [points[0]]
    current = 0
    for i in range(len(points) - 1):
        length = Vector.Distance(points[i], points[i + 1])

        i_step = step * modifier(len(new_points) / N)

        while current + i_step < length:
            current += i_step
            new_points.append(
                points[i] + (points[i + 1] - points[i]) * current / length,
            )

        current -= length

    new_points.append(points[-1])

    return new_points


class Animation:
    def __init__(self, start, keyframes):
        self.start = start
        self.keyframes = keyframes

    def __repr__(self):
        return f"Animation({self.start}, {len(self.keyframes)})"

    def get_frame(self, frame):
        idx = frame - self.start

        if idx < 0:
            return self.keyframes[0]
        elif idx >= len(self.keyframes):
            return self.keyframes[-1]
        else:
            return self.keyframes[idx]

    def __len__(self):
        return len(self.keyframes) + self.start


def find_connections(tendril, vein_no, threshold=1):
    vein = tendril[vein_no]
    connections = {}

    for i in range(len(vein) - 1):
        curr = vein[i]
        next = vein[i + 1]

        for j in range(vein_no + 1, len(tendril)):
            dist = distance_to_line(curr, next, tendril[j][0])
            if dist < threshold:
                if j not in connections:
                    connections[j] = (dist, i)
                else:
                    if dist < connections[j][0]:
                        connections[j] = (dist, i)

    for k in connections:
        d1 = Vector.Distance(vein[connections[k][1]], tendril[k][0])
        d2 = Vector.Distance(vein[connections[k][1] + 1], tendril[k][0])
        if d2 < d1:
            connections[k] = (connections[k][0], connections[k][1] + 1)

    return {connections[k][1]: k for k in connections}


def make_animations(tendril, vein_no, start=0):
    connections = find_connections(tendril, vein_no)
    animations = [Animation(start, tendril[vein_no])]

    for i in range(len(tendril[vein_no])):
        if i in connections:
            animations += make_animations(tendril, connections[i], start=start + i)

    return animations


def interpolate(tendril, scale=2):
    new_tendril = []
    for vein in tendril:
        length = line_length(vein)
        if len(vein) < 2:
            new_tendril.append(vein)
        else:
            new_tendril.append(piecewise(vein, N=length / 5 * scale))

    return new_tendril


def load_vein(path):
    veins = []

    with open(path, "r") as f:
        raw = f.read().split("\n")

    for vein in raw:
        if len(vein) == 0:
            continue

        this = []
        split = vein.split(",")
        if len(split) % 2 != 0:
            raise Exception("Invalid vein file")

        for i in range(0, len(split), 2):
            this.append(Vector(float(split[i]), float(split[i + 1])))

        veins.append(this)

    return normalize(make_animations(interpolate(veins, scale=1), 0))
