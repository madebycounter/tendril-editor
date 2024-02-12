from lib.vector import Vector


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
        start = round(self.start(), 2)
        end = round(self.end(), 2)
        return f"Animation({start} -> {end}, {len(self.keyframes)})"

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

    animations = [(tendril, animation)]
    for child in tendril.children:
        animations += make_animations_iter(child)

    return animations


def make_animations(source):
    anims = make_animations_iter(source)

    longest = max([a[1].end() for a in anims])
    for tendril, anim in anims:
        anim.transform_keyframes(lambda k: k / longest)

        parent_id = source.parent_of(tendril.id)
        if parent_id is not None:
            parent = source.get_by_id(parent_id)
            first = tendril[0]
            closest = min(parent.data, key=lambda p: Vector.Distance(first, p))
            anim[0].position = closest

    return [a[1] for a in anims]


if __name__ == "__main__":
    from tendril import Tendril

    p = "A:\\projects\\nava onti\\music videos\\vfx + sfx\\tendrils\\veins\\image1.vein"
    tendril = Tendril.load(p)

    print(tendril)

    animations = make_animations(tendril)
    print(animations)