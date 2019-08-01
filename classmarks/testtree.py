from anytree import NodeMixin, PreOrderIter, RenderTree
from anytree.render import AsciiStyle


class Assessment(NodeMixin):
    def __init__(self, name, group, parent=None, weight=1.0, date=""):
        self.name = name
        self.group = group
        self.parent = parent
        self.weight = weight
        self.date = date
        self.cls = self.__class__.__name__

    def __repr__(self):
        msg = "{}(name={}, group={}, weight={})"
        return msg.format(self.cls, self.name, self.group, self.weight)

    def update(self, **kwargs):
        if "name" in kwargs:
            self.name = kwargs["name"]
        if "weight" in kwargs:
            self.weight = kwargs["weight"]
        if "date" in kwargs:
            self.date = kwargs["date"]


class TestTree(NodeMixin):
    def __init__(self, name="Total"):
        self.name = name
        self.group = "root"
        self.weight = 1.0
        self.date = ""
        self.major_suffix = 1
        self.sub_suffix = 1
        self.test_suffix = 1
        self.cls = self.__class__.__name__

    def __repr__(self):
        msg = "{}(name={}, group={})"
        return msg.format(self.cls, self.name, self.group)

    def add(self, name=None, parent=None):
        if not parent or parent == self:
            parent = self
        group = self.get_group(parent)
        if name is None:
            name = self.get_name(parent, group)
        new_node = Assessment(name, group, parent)
        return new_node

    def delete(self, node):
        deleted_nodes = node.descendants
        node.parent = None
        del node
        return deleted_nodes

    def edit(self, node, **kwargs):
        node.update(**kwargs)
        return kwargs

    def get_name(self, parent, group):
        group = self.get_group(parent)
        num = str(self.get_group_num(group))
        return " ".join((group, num))

    def check_collision(self, name):
        names = [test.name for test in self]
        return bool(name in names)

    def get_group(self, parent):
        group = ""
        if parent.group == "root":
            group = "major"
        if parent.group == "major":
            group = "sub"
        if parent.group == "sub":
            group = "test"
        return group

    def get_index(self, ass):
        for index, item in enumerate(self):
            if item == ass:
                break
        return index

    def get_family(self, parent):
        family = [parent, *parent.descendants]
        return family

    def get_group_num(self, group):
        suffix = 0
        if group == "major":
            suffix = self.major_suffix
            self.major_suffix += 1
        if group == "sub":
            suffix = self.sub_suffix
            self.sub_suffix += 1
        if group == "test":
            suffix = self.test_suffix
            self.test_suffix += 1
        return suffix
        #return len([ass for ass in self if ass.group == group])

    def get_tree(self):
        return RenderTree(self, style=AsciiStyle())

    def __iter__(self):
        return PreOrderIter(self)

    def __len__(self):
        return len(self.descendants) + 1

    def __getitem__(self, index):
        return list(self)[index]
