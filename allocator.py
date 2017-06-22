#!//bin/env python
import functools

class decorators(object):
    @staticmethod
    def registerhooks(entry=[], exit=[], *args, **kwargs):
        """Registers some hooks for a function.
        Adds them as attributes under obj.__hooks."""
        def wrap(f):
            _kwargs = dict(kwargs)
            _kwargs.update({'entry': entry, 'exit': exit})
            def wrapped_f(*args, **kwargs):
                return f(*args, **kwargs)
            wrapped_f.__hooks = _kwargs
            return wrapped_f
        return wrap

    @staticmethod
    def processhooks(f):
        """Run the hooks if existing."""
        hooks = f.__hooks
        def wrapped(*args, **kwargs):
            for method in hooks.get('entry', []):
                method.__call__()
            ret = f(*args, **kwargs)
            for method in hooks.get('exit', []):
                method.__call__()
            return ret
        return wrapped

    @staticmethod
    def methodhooks(entry=[], exit=[], *args, **kwargs):
        """Registers some hooks for a function.
        Adds them as attributes."""
        def wrap(f):
            _kwargs = dict(kwargs)
            _kwargs.update({'entry': entry, 'exit': exit})
            @functools.wraps(f)
            @decorators.processhooks
            @decorators.registerhooks(entry, exit, *args, **kwargs)
            def wrapped_f(*args, **kwargs):
                 return f(*args, **kwargs)
            dump_magic(wrapped_f)
            return wrapped_f
        return wrap

class Handler(object):
    def __init__(self, ktenant, **kwargs):
        pass
    @staticmethod
    def set_quota(*args, **kwargs):
        print('* Setting quota. args=%s kwargs=%s' % (args, kwargs))
    @staticmethod
    def exit_hook(*args, **kwargs):
        print('* Running exit hook. args=%s kwargs=%s' % (args, kwargs))


def dump_magic(obj, **kwargs):
    attrs = ['__doc__', '__module__', '__name__']
    name = getattr(obj, '__name__', 'obj.__name__')
    for f in attrs:
        try:
            print('-- dump_magic::in %s() %s: %s' % (name, f, getattr(obj, f)))
        except: pass

class ResourceAllocator(object):
    class allocator:
        def __init__(self, f):
            self.f = f
            self.__name__ = f.__name__
            self.__doc__ = f.__doc__
            self.__module__ = f.__module__

        def __call__(self, *args, **kwargs):
            allocator = self._get_allocator(self.f, *args, **kwargs)
            print('Allocator name: %s' %  allocator.__name__)
            print('Allocator doc: %s' %  allocator.__doc__)
            return allocator()

        def _get_allocator(self, f, *args, **kwargs):
            """Generates an allocator function."""
            context = {
                'args': args,
                'kwargs': kwargs,
            }
            hooks = self._get_hooks(f, context=context)
            hook_decorator = decorators.methodhooks(**hooks)
            fn = hook_decorator(f)
            return fn

        def _get_hooks(self, f, context={}, **kwargs):
            hook_map = {}
            try:
                name = f.__name__
                # match hooks on name
                if name == '_create_resource':
                    kwargs = context['kwargs']
                    if kwargs.get('type') == 'PAID':
                        hook_map = {
                            # Probably need partials here
                            'entry': [Handler.set_quota],
                            'exit': [Handler.exit_hook],
                        }
            except:
                pass
            return hook_map


class Daemon(object):
    def init(self, *args, **kwargs):
        pass

    @ResourceAllocator.allocator
    def _create_resource(*args, **kwargs):
        """Create an resource."""
        print('Creating resource.')


if __name__ == '__main__':
    d = Daemon()
    print('Without matching context')
    d._create_resource(type=None)
    print('With matching context')
    d._create_resource(type='PAID')
    dump_magic(d._create_resource)

# vim: tw=79:sw=4:ts=4:shiftround:et
