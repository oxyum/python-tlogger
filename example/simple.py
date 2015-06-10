# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from tlogger import get_logger


logger = get_logger(__name__)


class EveryMethodLogged(object):
    field1 = 'value1'

    @logger
    def foo(self, arg):
        return 'EveryMethodLogged.foo %s' % arg

    @logger
    def bar(self, arg):
        return 'EveryMethodLogged.bar %s' % arg


class OnlySpam(object):
    field2 = 'value2'

    @logger
    def spam(self, arg):
        return 'OnlySpam.spam %s' % arg

    def eggs(self, arg):
        return 'OnlySpam.eggs %s' % arg


@logger
def power(left, right):
    return left ** right


def divide(left, right):
    with logger.start_action('division', params={'left': left}) as action:
        action.add_params(right=right)

        result = left / right

        action.add_result(result)

    return result


@logger
def safe_divide(left, right):
    if right == 0:
        logger.set_status(  # Nearest action in stack
            1, 'right argument of divide() can\'t be zero'
        )
        return None

    return left / right


@logger
def nested_actions(arg1, arg2):
    func_action = logger.action_for(nested_actions)

    func_action.add_param(foo='bar')

    with logger.start_action('nested-action') as nested_action:
        nested_action.add_result(arg1)
        func_action.add_arg(arg2)

    return 3412


def log_iterable(seq):
    """
    seq = [1, 2, 3]

    event=...iteration.start
    event=...iteration.step step=0 value=1
    event=...iteration.step step=1 value=2
    event=...iteration.step step=2 value=3
    event=...iteration.stop
    """
    for item in logger.iter(seq, steps=True):  # steps=True to turn step logging on
        pass  # do_stuff()


def log_context_manager():
    """
    event=...context_manager.start obj=<open file '/tmp/foobar.txt', mode 'r' at 0x7efc8bbcfc00>
    event=...context_manager.enter
    event=...context_manager.exit exception=False
    """
    name = '/tmp/foobar.txt'
    with logger.context(open(name, 'rw')) as f:
        f.read()


if __name__ == '__main__':
    eml = EveryMethodLogged()
    val1 = eml.field1

    logger.dump(val1=val1)

    eml.foo(val1)
    eml.bar(val1)

    osp = OnlySpam()
    val2 = osp.field2

    logger.dump(val2=val2)

    osp.spam(val2)
    osp.eggs(val2)

    power(2, 126)

    divide(2, 3)

    logger.debug('Gonna divide %s by zero!', 2)
    try:
        divide(2, 0)
    except ZeroDivisionError:
        pass

    safe_divide(3, 0)

    nested_actions(32, 54)

    log_iterable([1, 2, 3, 4, 5])

    log_context_manager()
