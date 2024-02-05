from load import load_vein
from lib.vector import Vector, distance_to_line
from lib.transform import line_length, piecewise


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


class Path:
    def __init__(self, path, children=[]):
        self.path = path
        self.children = children


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


def make_path(tendril, vein_no, start=0):
    vein = tendril[vein_no]
    connections = find_connections(tendril, vein_no)

    children = []
    path = []
    for i in range(start, len(vein)):
        if i in connections:
            children.append(make_path(tendril, connections[i]))
            children.append(make_path(tendril, vein_no, i + 1))
            break
        else:
            path.append(vein[i])

    return Path(path, children)


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
