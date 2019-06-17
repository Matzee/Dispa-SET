class Task(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *inputs):
        return Job(self, inputs)


class Input(object):
    def __init__(self, value):
        self._value = value
        self.outputs = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value == value:
            return
        self._value = value
        for output in self.outputs:
            output.dirty()

    def __str__(self):
        return '<{} value={}>'.format(type(self).__name__, self._value)

    __repr__ = __str__


PENDING = object()


class Job(object):
    def __init__(self, task, inputs):
        self.task = task
        self.inputs = inputs
        self.outputs = []
        self._value = PENDING
        for input in inputs:
            input.outputs.append(self)

    def dirty(self):
        if self._value is PENDING:
            return
        self._value = PENDING
        for output in self.outputs:
            output.dirty()

    @property
    def value(self):
        if self._value is PENDING:
            try:
                self._value = self.task.func(
                    *(input.value for input in self.inputs)
                )
            except Exception as e:
                msg = 'Job {} failed'.format(self.task.func)
                raise RuntimeError(msg) from e
        return self._value

    def __str__(self):
        return '<{} func={}>'.format(
            type(self).__name__, self.task.func.__name__
        )

    __repr__ = __str__


def trace(name):
    def tracer(arg):
        print('invoke {} with arg {}'.format(name, arg))
        return arg

    return tracer


a = Input(0)
b = Input(1)
ta = Task(trace('a'))(a)
tb = Task(trace('b'))(b)
import operator
c = Task(operator.add)(ta, tb)
d = Task(trace('d'))(ta)

print('---')
print(c.value)
print(d.value)
print('---')
print(c.value)
print(d.value)
print('---')
a.value = 1
print(c.value)
print(d.value)
