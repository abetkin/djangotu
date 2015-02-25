import abc
from functools import reduce
import operator
from django.db.models.query import Q
from declared import Mark, DeclaredMeta

class qobj:
    def __init__(self, qobj):
        self.qobj = qobj

    def filter(self, queryset):
        return queryset.filter(self.qobj)

    def __repr__(self):
        pairs = ['%s=%s' % item for item in self.qobj.children]
        return 'Q: %s' % ', '.join(pairs)


class qsfilter(Mark):
    collect_into = '_declared_filters'

    def __init__(self, func):
        self.func = func

    def __repr__(self):
        return self.func.__doc__ or self.func.__name__

    def filter(self, queryset):
        return self.func(queryset)

    def build(mark, *args):
        if isinstance(mark, Q):
            return qobj(mark)
        return mark

qsfilter.register(Q)

@qsfilter.register
class FiltersDeclaredMeta(DeclaredMeta, abc.ABCMeta):

    def __repr__(cls):
        return ', '.join(cls._declared_filters.keys())


class DeclaredFilters(metaclass=FiltersDeclaredMeta):

    default_mark = qsfilter

    @classmethod
    def filter(cls):
        raise NotImplementedError()


class ReducedFilters(DeclaredFilters):

    @classmethod
    def filter(cls, queryset):
        filters = [f.filter(queryset)
                   for f in cls._declared_filters.values()]
        if filters:
            return reduce(cls.operation, filters)
        return queryset


class qand(ReducedFilters):
    operation = operator.and_

class qor(ReducedFilters):
    operation = operator.or_


class CascadeFilter(DeclaredFilters):

    @classmethod
    def filter(cls, objects=None):
        if objects is None:
            objects = cls.objects
        for f in cls._declared_filters.values():
            objects = f.filter(objects)
        return objects
