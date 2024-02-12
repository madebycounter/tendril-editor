from load import load_vein
from lib.vector import Vector, distance_to_line
from lib.transform import line_length, piecewise


class State:
    def __init__(self, position, rotation, scale, visible):
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.visible = visible

    def __repr__(self):
        visibility = "Visible" if self.visible else "Hidden"
        return f"State({visibility}, {self.position}, {self.rotation}, {self.scale})"

    def interpolate(self, target, percent):
        return State(
            Vector.Lerp(self.position, target.position, percent),
            self.rotation + (target.rotation - self.rotation) * percent,
            self.scale + (target.scale - self.scale) * percent,
            self.visible,
        )


class Animation:
    def __init__(self, keyframes=None):
        self.keyframes = keyframes or {}

    def __repr__(self):
        return f"Animation({self.start()}-{self.end()}, {len(self.keyframes)})"

    def get_state(self, time):
        if time in self.keyframes:
            return self.keyframes[time]

        all_before = [k for k in self.keyframes if k < time]
        all_after = [k for k in self.keyframes if k > time]

        if len(all_before) == 0:
            return self.keyframes[min(self.keyframes)]

        if len(all_after) == 0:
            return self.keyframes[max(self.keyframes)]

        before = min(all_before, key=lambda k: time - k)
        after = min(all_after, key=lambda k: k - time)

        percent = (time - before) / (after - before)
        return self.keyframes[before].interpolate(self.keyframes[after], percent)

    def __getitem__(self, idx):
        return self.get_state(idx)

    def __setitem__(self, idx, value):
        self.keyframes[idx] = value

    def start(self):
        return min(self.keyframes.keys())

    def end(self):
        return max(self.keyframes.keys())

    def __len__(self):
        return self.end() - self.start()

    def __iter__(self):
        return iter(self.keyframes)

    def transform_keyframes(self, func):
        new_keyframes = {}
        for kf in self.keyframes:
            new_keyframes[func(kf)] = self.keyframes[kf]
        self.keyframes = new_keyframes


def make_animations_iter(tendril, start=0):
    animation = Animation()
    kf = start
    for i in range(len(tendril) - 1):
        curr = tendril[i]
        next = tendril[i + 1]
        animation[kf] = State(curr, 0, 1, True)
        kf += Vector.Distance(curr, next)

    animations = [animation]
    for child in tendril.children:
        animations += make_animations_iter(child)

    return animations


def make_animations(tendril):
    anims = make_animations_iter(tendril)

    longest = max([a.end() for a in anims])
    for anim in anims:
        anim.transform_keyframes(lambda k: k / longest)

    return anims


# tendril = load_vein(
#     "A:\\projects\\nava onti\\music videos\\vfx + sfx\\tendrils\\veins\\image1.vein"
# )

# animations = make_animations(tendril)
# print(animations)

# def find_connections(tendril, vein_no, threshold=1):
#     vein = tendril[vein_no]
#     connections = {}

#     for i in range(len(vein) - 1):
#         curr = vein[i]
#         next = vein[i + 1]

#         for j in range(vein_no + 1, len(tendril)):
#             dist = distance_to_line(curr, next, tendril[j][0])
#             if dist < threshold:
#                 if j not in connections:
#                     connections[j] = (dist, i)
#                 else:
#                     if dist < connections[j][0]:
#                         connections[j] = (dist, i)

#     for k in connections:
#         d1 = Vector.Distance(vein[connections[k][1]], tendril[k][0])
#         d2 = Vector.Distance(vein[connections[k][1] + 1], tendril[k][0])
#         if d2 < d1:
#             connections[k] = (connections[k][0], connections[k][1] + 1)

#     return {connections[k][1]: k for k in connections}


# def make_path(tendril, vein_no, start=0):
#     vein = tendril[vein_no]
#     connections = find_connections(tendril, vein_no)

#     children = []
#     path = []
#     for i in range(start, len(vein)):
#         if i in connections:
#             children.append(make_path(tendril, connections[i]))
#             children.append(make_path(tendril, vein_no, i + 1))
#             break
#         else:
#             path.append(vein[i])

#     return Path(path, children)


# def make_animations(tendril, vein_no, start=0):
#     connections = find_connections(tendril, vein_no)
#     animations = [Animation(start, tendril[vein_no])]

#     for i in range(len(tendril[vein_no])):
#         if i in connections:
#             animations += make_animations(tendril, connections[i], start=start + i)

#     return animations


# def interpolate(tendril, scale=2):
#     new_tendril = []
#     for vein in tendril:
#         length = line_length(vein)
#         if len(vein) < 2:
#             new_tendril.append(vein)
#         else:
#             new_tendril.append(piecewise(vein, N=length / 5 * scale))

#     return new_tendril
