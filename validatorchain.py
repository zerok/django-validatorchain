class ChainElement(object):
    def __init__(self, validator, skip_on_error=None):
        if skip_on_error is None:
            skip_on_error = False
        self.validator = validator
        self.skip_on_error = skip_on_error

    def __call__(self, *args, **kwargs):
        return self.validator(*args, **kwargs)


class ChainIterator(object):
    def __init__(self, chain):
        self.chain = chain
        self._iter = iter(self.chain._data)
        self._has_error = False

    def __next__(self):
        return self.next()

    def next(self):
        next_item = next(self._iter)
        if next_item.skip_on_error and self._has_error:
            return next(self)

        def func(*args, **kwargs):
            try:
                return next_item(*args, **kwargs)
            except Exception as e:
                self._has_error = True
                raise e
        return func


class ValidatorChain(object):
    def __init__(self):
        self._data = []

    def add(self, validator, skip_on_error=None):
        if isinstance(validator, ChainElement):
            self._data.append(validator)
        else:
            self._data.append(ChainElement(validator, skip_on_error))
        return self

    def __iter__(self):
        return ChainIterator(self)

    def __len__(self):
        return len(self._data)

    def __radd__(self, other):
        result = ValidatorChain()
        if isinstance(other, ValidatorChain):
            for val in other._data:
                result.add(val)
        else:
            for val in other:
                result.add(val)
        for val in self._data:
            result.add(val)
        return result

    def __add__(self, other):
        result = ValidatorChain()
        for val in self._data:
            result.add(val)
        if isinstance(other, ValidatorChain):
            for val in other._data:
                result.add(val)
        else:
            for val in other:
                result.add(val)
        return result
