import pickle
import uuid


class Tendril:
    def __init__(self, width=1, data=None, children=None, id=None):
        self.width = width
        self.data = data or []
        self.children = children or []
        self.id = id or uuid.uuid4()

    def get_by_id(self, uid):
        if uid == self.id:
            return self
        for child in self.children:
            found = child.get_by_id(uid)
            if found is not None:
                return found

    def parent_of(self, uid):
        for child in self.children:
            if child.id == uid:
                return self.id
            found = child.parent_of(uid)
            if found is not None:
                return found

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def __repr__(self):
        return f"Tendril({str(self.id)[-5:]}, {len(self)}, {len(self.children)})"

    def __str__(self) -> str:
        if len(self.children) == 0:
            return repr(self)
        children = [str(d) for d in self.children]
        string = repr(self) + " ["
        for child in children:
            for idx, line in enumerate(child.split("\n")):
                string += "\n    %s" % line
        return string + "\n]"

    def __getitem__(self, idx):
        return self.data[idx]

    def __setitem__(self, idx, value):
        self.data[idx] = value

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def append(self, value):
        self.data.append(value)

    def insert(self, idx, value):
        self.data.insert(idx, value)

    def remove(self, value):
        self.data.remove(value)

    def pop(self, idx=-1):
        return self.data.pop(idx)

    def encode(self):
        return pickle.dumps(self)

    def copy(self):
        return Tendril(
            width=self.width,
            data=self.data.copy(),
            children=[child.copy() for child in self.children],
            id=self.id,
        )

    def all(self):
        individuals = [self]
        for child in self.children:
            individuals += child.all()
        return individuals

    @staticmethod
    def load(path):
        with open(path, "rb") as file:
            return pickle.load(file)
