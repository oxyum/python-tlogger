# -*- coding: utf-8 -*-
'''
module: method_decorator
author: denis@ryzhkov.org
license: free
'''

all = [
    'method_decorator',
    'version',
]

version = 1

#### method_decorator

class method_decorator(object):

    '''
    Abstract decorator that knows details about method, e.g. class where method is bound, that is None if method is plain function.
    Also hides decorator traces by answering to system attributes more correctly than functools.wraps() does.
    Tested with: instance-methods, class-methods, static-methods, and plain functions.
    Inherit and override any behaviour.

    Usage:
        class my_dec(method_decorator):
            def __call__(self, *args, **kwargs):

                print('Calling %(method_type)s %(method_name)s from instance %(instance)s class %(class_name)s from module %(module_name)s with args %(args)s and kwargs %(kwargs)s.' % dict(
                    method_type=self.method_type,
                    method_name=self.__name__,
                    instance=self.obj,
                    class_name=(self.cls.__name__ if self.cls else None),
                    module_name=self.__module__,
                    args=args,
                    kwargs=kwargs,
                ))

                return method_decorator.__call__(self, *args, **kwargs)
        @my_dec
        def func_or_method(...
    '''

    def __init__(self, func, obj=None, cls=None, method_type='function'): # defaults are ok for plain functions, and will be changed by __get__ for methods
        self.func, self.obj, self.cls, self.method_type = func, obj, cls, method_type

    def __get__(self, obj=None, cls=None): # is called as method: Cls.func or obj.func
        if self.obj == obj and self.cls == cls: return self # use same instance, if it was already switched by previous __get__

        if isinstance(self.func, staticmethod): method_type = 'staticmethod' # later __get__ unwraps staticmethod object to plain function
        elif isinstance(self.func, classmethod): method_type = 'classmethod' # later Cls.classm is same as Cls.instancem(obj,..
        else: method_type = 'instancemethod' # can't rely on obj in call like Cls.instancem(obj,..

        return object.__getattribute__(self, '__class__')(# use specialized decorator instance, don't change current instance attributes - it leads to conflicts
            self.func.__get__(obj, cls), obj, cls, method_type) # use func's method version, [un]bound to [None-able] obj and cls.

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __getattribute__(self, attr_name): # hiding traces
        if attr_name in ('__init__', '__get__', '__call__', '__getattribute__', 'func', 'obj', 'cls', 'method_type'): # our known names, our '__class__' is used only once with explicit object.__getattribute__
            return object.__getattribute__(self, attr_name) # stopping recursion
        # all other attr_names, that can be auto-defined by system in self, and all others, are searched in self.func, e.g.: __module__, __class__, __name__, __doc__, im_*, func_*, etc.
        return getattr(self.func, attr_name) # raises AttributeError if name not found in self.func

    def __repr__(self): # ignores __getattribute__
        return self.func.__repr__()

#### test

if __name__ == '__main__':

    class my_dec(method_decorator):
        def __call__(self, *args, **kwargs):

            print('Calling %(method_type)s %(method_name)s from instance %(instance)s class %(class_name)s from module %(module_name)s with args %(args)s and kwargs %(kwargs)s.' % dict(
                method_type=self.method_type,
                method_name=self.__name__,
                instance=self.obj,
                class_name=(self.cls.__name__ if self.cls else None),
                module_name=self.__module__,
                args=args,
                kwargs=kwargs,
            ))

            return method_decorator.__call__(self, *args, **kwargs)

    class A(object):

        @my_dec
        def m(self, x):

            '''Test doc.'''

            print('m:', self, x)
            return x

        @my_dec
        @classmethod
        def cm(cls, x):
            print('cm:', cls, x)
            return x

        @my_dec
        @staticmethod
        def sm(x):
            print('sm:', x)
            return x

    class C(A):
        pass

    @my_dec
    def f(x):
        print('f:', x)
        return x

    @my_dec
    def f2():
        return ""

    print(1, C().m)
    print(2, C().m.__module__)
    print(3, C().m.__name__)
    print(4, C().m.__doc__)
    print(5, C().m.im_class)
    print(6, C().m.im_self)
    print(7, C().m.im_func)
    print(8, C().m('ok'))
    print(9, C.m(C(), 'ok'))
    print(10, C.cm)
    print(11, C.cm('ok'))
    print(12, C().cm('ok'))
    print(13, C.sm)
    print(14, C.sm('ok'))
    print(15, C().sm('ok'))
    print(16, f)
    print(17, f('ok'))

    print(18, f2)
    print(19, f2())
