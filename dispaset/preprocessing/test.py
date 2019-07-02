import pandas as pd
from collections.abc import Iterable


class Set():

    def __init__(self, name, data):
        self.name = name
        if isinstance(data[0], Iterable):
            2+"a"
            #nested iterable

        if len(set(data)) < len(data):
            print("your set contains duplicates")
        self.data = pd.Series(data)

    def __iter__(self):
        self.n = 0
        return self


    def __next__(self):
        if self.n <= len(data):
            self.n += 1
            return data[self.n + 1]
        else:
            raise StopIteration


class Parameter():

    def __init__(self, data, default_parameter, sets, data_path=None):

        self.sets = pd.DataFrame(index=sets)
        self.data = pd.DataFrame(data)

        def get_dim(self):
            return self.data.MultiIndex.nlevels

    def __getitem__(self, sliced):
        self.data.loc[sliced]

