from unittest.mock import (
    patch as s_patch, MagicMock, _patch as _s_patch, _get_target, _is_started, _builtins, ModuleType,
    create_autospec, _is_list, _is_instance_mock, _instance_callable, NonCallableMagicMock, NonCallableMock)
import sys
from functools import wraps


def AsyncMock(*args, **kwargs):
    m = MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)
    mock_coro.mock = m
    return mock_coro


class _patch(_s_patch):
    def decorate_callable(self, func):
        if hasattr(func, 'patchings'):
            func.patchings.append(self)
            return func

        @wraps(func)
        def patched(*args, **keywargs):
            extra_args = []
            entered_patchers = []

            exc_info = tuple()
            try:
                for patching in patched.patchings:
                    arg = patching.__enter__()
                    entered_patchers.append(patching)
                    if patching.attribute_name is not None:
                        keywargs.update(arg)
                    elif patching.new:  # replaced this from elif patching.new is DEFAULT:
                        extra_args.append(patching.new)

                args += tuple(extra_args)
                patched.args2_0 = args
                return func(*args, **keywargs)
            except:
                if (patching not in entered_patchers and
                        _is_started(patching)):
                    # the patcher may have been started, but an exception
                    # raised whilst entering one of its additional_patchers
                    entered_patchers.append(patching)
                # Pass the exception to __exit__
                exc_info = sys.exc_info()
                # re-raise the exception
                raise
            finally:
                for patching in reversed(entered_patchers):
                    patching.__exit__(*exc_info)
        patched.patchings = [self]
        return patched


def patch(
    target, new=None, return_value=None, spec=None, create=False,
    spec_set=None, autospec=None, new_callable=None, **kwargs
):
    getter, attribute = _get_target(target)
    new2 = AsyncMock()
    return _patch(
        getter, attribute, new2, spec, create,
        spec_set, autospec, new_callable, kwargs
    )
