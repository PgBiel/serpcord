__all__ = ("init_model_from_mapping_json_data",)

import typing
import inspect
import collections

from serpcord.exceptions import APIJsonParsedTypeMismatchException, APIJsonParseException, APIDataParseException
from serpcord.models.apimodel import JsonAPIModel
from typing import Optional, TypeVar, Mapping, Any, Type, Dict, Callable, List, Iterable, Union, Tuple

T = TypeVar("T", bound=JsonAPIModel[Mapping[str, Any]])


def _get_annotation_port(obj, *, globals=None, locals=None, eval_str=False):
    """Compute the annotations dict for an object.
    obj may be a callable, class, or module.
    Passing in an object of any other type raises TypeError.
    Returns a dict.  get_annotations() returns a new dict every time
    it's called; calling it twice on the same object will return two
    different but equivalent dicts.
    This function handles several details for you:
      * If eval_str is true, values of type str will
        be un-stringized using eval().  This is intended
        for use with stringized annotations
        ("from __future__ import annotations").
      * If obj doesn't have an annotations dict, returns an
        empty dict.  (Functions and methods always have an
        annotations dict; classes, modules, and other types of
        callables may not.)
      * Ignores inherited annotations on classes.  If a class
        doesn't have its own annotations dict, returns an empty dict.
      * All accesses to object members and dict values are done
        using getattr() and dict.get() for safety.
      * Always, always, always returns a freshly-created dict.
    eval_str controls whether or not values of type str are replaced
    with the result of calling eval() on those values:
      * If eval_str is true, eval() is called on values of type str.
      * If eval_str is false (the default), values of type str are unchanged.
    globals and locals are passed in to eval(); see the documentation
    for eval() for more information.  If either globals or locals is
    None, this function may replace that value with a context-specific
    default, contingent on type(obj):
      * If obj is a module, globals defaults to obj.__dict__.
      * If obj is a class, globals defaults to
        sys.modules[obj.__module__].__dict__ and locals
        defaults to the obj class namespace.
      * If obj is a callable, globals defaults to obj.__globals__,
        although if obj is a wrapped function (using
        functools.update_wrapper()) it is first unwrapped.
    """
    import sys
    import types
    import functools
    if isinstance(obj, type):
        # class
        obj_dict = getattr(obj, '__dict__', None)
        if obj_dict and hasattr(obj_dict, 'get'):
            ann = obj_dict.get('__annotations__', None)
            if isinstance(ann, types.GetSetDescriptorType):
                ann = None
        else:
            ann = None

        obj_globals = None
        module_name = getattr(obj, '__module__', None)
        if module_name:
            module = sys.modules.get(module_name, None)
            if module:
                obj_globals = getattr(module, '__dict__', None)
        obj_locals = dict(vars(obj))
        unwrap = obj
    elif isinstance(obj, types.ModuleType):
        # module
        ann = getattr(obj, '__annotations__', None)
        obj_globals = getattr(obj, '__dict__')
        obj_locals = None
        unwrap = None
    elif callable(obj):
        # this includes types.Function, types.BuiltinFunctionType,
        # types.BuiltinMethodType, functools.partial, functools.singledispatch,
        # "class funclike" from Lib/test/test_inspect... on and on it goes.
        ann = getattr(obj, '__annotations__', None)
        obj_globals = getattr(obj, '__globals__', None)
        obj_locals = None
        unwrap = obj
    else:
        raise TypeError(f"{obj!r} is not a module, class, or callable.")

    if ann is None:
        return {}

    if not isinstance(ann, dict):
        raise ValueError(f"{obj!r}.__annotations__ is neither a dict nor None")

    if not ann:
        return {}

    if not eval_str:
        return dict(ann)

    if unwrap is not None:
        while True:
            if hasattr(unwrap, '__wrapped__'):
                unwrap = unwrap.__wrapped__
                continue
            if isinstance(unwrap, functools.partial):
                unwrap = unwrap.func
                continue
            break
        if hasattr(unwrap, "__globals__"):
            obj_globals = unwrap.__globals__

    if globals is None:
        globals = obj_globals
    if locals is None:
        locals = obj_locals

    return_value = {key:
        value if not isinstance(value, str) else eval(value, globals, locals)
        for key, value in ann.items() }
    return return_value


if hasattr(typing, "Literal"):
    LiteralTrue = typing.Literal[True]
    LiteralFalse = typing.Literal[False]
else:
    LiteralTrue = LiteralFalse = bool


# _GenericAlias = typing.cast(Any, getattr(typing, "_GenericAlias", type))

def _typing_generic_converter(T: Any, *, recursive: bool = True) -> Union[type, Tuple[type, ...]]:
    """Simplifies special types for an :func:`isinstance` check to work.
    Converts ``typing.Union[A, B, C, ...]`` into the tuple ``(A, B, C, ...)``;
    ``typing.Optional[T]`` into the tuple ``(T, NoneType)``;
    and any subscripted generic type (in the form ``C[T]``) into the original, non-subscripted class
    (``C``).
    If the given type is not one of the aforementioned special types, then it is returned unchanged.

    Args:
        T (:class:`type`): Special type to simplify (see above).
        recursive (:class:`bool`, optional): If ``True``, then, if the given type (arg ``T``) is a Union or Optional,
            applies this function recursively on the elements of the resulting tuple of arguments, simplifying any
            further generic subscriptions. Defaults to ``True``. (If ``False``, resulting tuple elements can't be
            guaranteed to be types, as they can be generic subscriptions instead.)

    Returns:
        Union[:class:`type`, Tuple[:class:`type`, ...]]: The simplified type(s). If the given type was not
        :class:`typing.Union`, :class:`typing.Optional` or a subscripted generic type, then it is returned
        unchanged.

    Examples:
        .. testsetup:: *

            import typing
            from serpcord.utils.model import _typing_generic_converter
        .. doctest::

            >>> _typing_generic_converter(typing.Union[str, int, bool])  # str, int, or bool, as a tuple
            (<class 'str'>, <class 'int'>, <class 'bool'>)
            >>> _typing_generic_converter(typing.Optional[dict])  # dict or None, as a tuple
            (<class 'dict'>, <class 'NoneType'>)
            >>> S = typing.TypeVar("S")
            >>> class ExampleGenericType(typing.Generic[S]):
            ...     pass
            >>> _typing_generic_converter(ExampleGenericType[str])  # removes subscription
            <class 'ExampleGenericType'>
            >>> _typing_generic_converter(typing.Union[ExampleGenericType[str], int])  # recursive simplification
            (<class 'ExampleGenericType'>, <class 'int'>)
            >>> _typing_generic_converter(typing.Union[ExampleGenericType[str], int], recursive=False)
            (ExampleGenericType[str], <class 'int'>)
    """
    gen_alias = getattr(typing, "_GenericAlias", None)
    origin_type = getattr(T, "__origin__", None)
    if origin_type == typing.Union:
        resulting_tuple: Tuple[type, ...] = getattr(T, "__args__", tuple())  # Union[A, B, C] -> (A, B, C)
        if recursive and isinstance(resulting_tuple, tuple):  # Union[C[T], D[C[Z]]] -> (C, D)
            return typing.cast(
                Tuple[type],
                tuple(_typing_generic_converter(T_, recursive=True) for T_ in resulting_tuple)
            )
            # note: Union[Union[Union[...]]] is already automatically simplified by the typing module, so no worries
            # about nested tuples.
        else:
            return resulting_tuple
    elif isinstance(origin_type, type) and isinstance(gen_alias, type) and isinstance(T, gen_alias):
        return origin_type  # C[T] -> C
    else:
        return T


def init_model_from_mapping_json_data(
    cls: Type[T], json_data: Mapping[str, Any],
    *, rename: Optional[Mapping[str, str]] = None, type_check_types: Union[bool, Iterable[Any]] = False
) -> T:
    """Generic function for instantiating :class:`~.JsonAPIModel` subclasses
    from given JSON :class:`dict` (Mapping) data. Works by taking keys from the received JSON data and passing them as
    parameters to the model's ``__init__`` function, with additional checks along the way.

    Args:
        cls (Type[``T``]): The class of the model that should be instantiated, hereby represented by ``T``.
        json_data (Mapping[:class:`str`, Any]): The JSON data to convert to a model instance (a Mapping/:class:`dict`).
        rename (Optional[Mapping[:class:`str`, :class:`str`]], optional): A Mapping/:class:`dict` to map keys received
            from the API to valid init parameter names. (Defaults to ``None`` - no additional mapping is
            done, and only ``json_data`` keys that are also valid ``cls.__init__`` parameters will be considered - other
            keys will be ignored.)
        type_check_types (Union[:class:`bool`, Iterable[:class:`type`]], optional): An optional list of types for
            which type checks should be run, or ``True`` to run type checks for all parameter types.
            I.e., if type ``T`` is in this list (or ``True`` was given), then, for every parameter in
            ``cls.__init__`` that is annotated to expect a value of type ``T`` (which includes all init parameters,
            if ``True`` was given), this function will run an ``isinstance`` check on the
            value of same key (post-renaming) given by the API (in ``json_data``)
            to make sure said value is a valid ``T``. In other words, ``type_check_types`` indicates that each parameter
            to ``cls.__init__`` whose type is in ``type_check_types`` (or all of them, if ``True`` was given instead
            of an Iterable of types) should have their corresponding value be type-checked before the init is actually
            run to ensure the init method won't receive unexpected value types (if there is a type mismatch,
            :exc:`~.APIJsonParsedTypeMismatchException` is raised). (Defaults to ``False``, meaning no type
            check will be run by default, leaving up to the ``__init__`` function to make sure parameters' types
            are OK.)

            .. note::
                If ``T`` is of the form :class:`typing.Union` or :class:`typing.Optional`
                (equivalent to Union[something, None]), then
                this check will accept any value within the Union's possibilities. I.e., for a parameter
                of type ``Union[A, B, C]``, the check will accept values of type ``A``, ``B``, or ``C``, and error
                for other types; for a parameter of type ``Optional[T]``, the check will accept either ``None`` or
                a value of type ``T``, and error for other types.

    Returns:
        ``T``: The constructed model (instance of ``cls``, constructed through ``cls.__init__``).

    Raises:
        :exc:`APIJsonParseException`: If the given ``json_data`` had unexpected parameter values/types.

    Examples:
        .. testsetup:: *

            from serpcord.utils.model import init_model_from_mapping_json_data
        .. doctest::

            >>> from serpcord.models.permissions import PermissionOverwrite
            >>> json_data = { "id": 123, "type": 1, "allow": 0, "deny": 1048580 }
            >>> PermissionOverwrite.from_json_data(json_data)
            PermissionOverwrite(target_id=Snowflake(value=123), overwrite_type=<PermissionOverwriteType.MEMBER: 1>, \
allow=<PermissionFlags.NONE: 0>, deny=<PermissionFlags.CONNECT|BAN_MEMBERS: 1048580>)
    """
    if not isinstance(cls, type):
        raise TypeError("'cls' must be a class.")

    if not isinstance(json_data, collections.Mapping):
        raise APIJsonParsedTypeMismatchException(
            f"Unexpected {cls.__qualname__} JSON data received (expected dict/Mapping; \
got {type(json_data).__qualname__})."
        )

    init_method: Callable = cls.__init__

    if not callable(init_method):
        raise TypeError("Given class' init isn't callable (?).")

    signature: inspect.Signature = inspect.signature(init_method)  # get init signature
    params = signature.parameters  # get init params

    # True if init accepts **kwargs; False otherwise
    accepts_kwargs = bool([param for param in params.values() if param.kind == inspect.Parameter.VAR_KEYWORD])

    # Possible param names in init
    expected_keys = list(params.keys())

    # Param annotations (form { param_name: expected_type })
    annotations: Dict[str, Any] = _get_annotation_port(init_method, eval_str=True)

    # key/values given through json_data (and parsed/renamed)
    received_params: Dict[str, Any] = dict()
    for k, v in json_data.items():
        renamed = rename.get(k, k) if rename is not None else k  # rename according to map
        if accepts_kwargs or renamed in expected_keys:  # is valid param name (or **kwargs is present => any name's OK)
            possible_json_model = annotations.get(renamed, None)  # get the param's type annotation (a possible
            converted_type: Optional[Union[type, Tuple[type, ...]]] = None         # JSON model to be parsed from data)
            # possible_json_models: List[Type[JsonAPIModel]] = []
            gen_alias = getattr(typing, "_GenericAlias")  # <- type for objects of form C[T], where C and T are types
            set_value: Any = v  # post-JSON model parsing value
            pjm_is_type_or_gen_alias = False  # True if possible_json_model is a type or Generic alias (C or C[T])
            if (
                isinstance(possible_json_model, type)  # form C
                or (isinstance(gen_alias, type) and isinstance(possible_json_model, gen_alias))  # form C[T]
            ):
                pjm_is_type_or_gen_alias = True
                converted_type = _typing_generic_converter(possible_json_model)  # reduce C[T] to C; Union[A, B, ...]
                last_error: Optional[Exception] = None                           # to (A, B, ...); Optional[T] to T
                if isinstance(converted_type, tuple):  # multiple possible types for this parameter (Union[A,B,...])
                    has_non_jsonapimodel: bool = False  # True if one of the possible types is not a JsonAPIModel
                    for possible_type in converted_type:  # go through each type; attempt to parse
                        if isinstance(possible_type, type):
                            if isinstance(v, possible_type):
                                break  # done, v already has a compatible type.
                            elif issubclass(possible_type, JsonAPIModel):
                                try:
                                    set_value = possible_type.from_json_data(v)
                                    break
                                except (APIDataParseException, TypeError) as e:
                                    last_error = e
                            else:
                                # -> since a Non-JsonAPIModel type is possible, don't error for mismatched type
                                # (Non-JsonAPIModel type checking is done later with
                                # the type_check_types parameter)
                                has_non_jsonapimodel = True
                    else:  # JSON data received did not fit into any of the possible types.
                        if not has_non_jsonapimodel:  # all are jsonapimodels and all conversion attempts failed
                            json_error = APIJsonParseException(  # -> raise
                                f"Unexpected {cls.__qualname__} JSON data received. \
(Key: {repr(k)}; Received: {repr(v)}, of type {type(v).__qualname__}; Failed to parse to {repr(possible_json_model)})"
                            )
                            if last_error is not None and isinstance(last_error, Exception):  # get last parse failure
                                raise json_error from last_error
                            else:
                                raise json_error
                elif (  # parameter type is not a Union - it's a single type -, so just run a simple isinstance check
                    isinstance(converted_type, type)  # to then proceed to convert to the relevant JsonAPIModel,
                    and issubclass(converted_type, JsonAPIModel)  # if necessary
                    and not isinstance(v, converted_type)         # (This isn't exactly a typecheck - it just converts
                ):                                                # raw data to JsonAPIModel when a subclass of it
                    set_value = converted_type.from_json_data(v)  # is expected. Then, typechecking is a consequence)

            if (  # begin typechecking.
                pjm_is_type_or_gen_alias
                and converted_type is not None
                and (
                    type_check_types is True  # check all types... or just this one
                    or isinstance(type_check_types, collections.Iterable) and possible_json_model in type_check_types
                )
                and not isinstance(set_value, converted_type)  # not expected instance! => raise. (failed type check)
            ):
                parsed_txt = f", parsed into a {type(set_value).__qualname__}" if type(v) != type(set_value) else ""
                raise APIJsonParsedTypeMismatchException(
                    f"Unexpected {cls.__qualname__} JSON data received. \
(Key: {repr(k)}; Expected a {repr(possible_json_model)}; Received a {type(v).__qualname__}{parsed_txt})."
                )

            # ok, JsonAPIModel parsing done, typechecking done. We may now use the resulting object.
            received_params[renamed] = set_value

    pos_args: List[Any] = list()  # pos args to pass to init
    kwargs: Dict[str, Any] = dict()  # kwargs to pass to init
    if accepts_kwargs:  # init accepts **kwargs
        for k, v in received_params.items():  # then only append pos args for pos-only args. Everything else: kwargs
            if k in params:
                param = params[k]
                if param.kind == param.POSITIONAL_ONLY:
                    pos_args.append(v)
                elif param.kind == param.VAR_POSITIONAL:
                    raise TypeError("*args and **kwargs simultaneously in JsonAPIModel init is forbidden.")
                elif param.kind == param.VAR_KEYWORD:
                    if isinstance(v, collections.Mapping):
                        kwargs.update(v)  # prob have to expand given dict
                    else:
                        kwargs[k] = v  # can't do, so just set it
                else:
                    kwargs[k] = v
            else:
                kwargs[k] = v  # will go in the func's kwargs
    else:  # init doesn't accept **kwargs => go through each parameter to check if they're pos-only or whatever else
        for param_name, parameter in params.items():
            if param_name in received_params:
                received_val = received_params[param_name]
                if parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD):
                    pos_args.append(received_val)
                elif parameter.kind == parameter.VAR_POSITIONAL:
                    if isinstance(received_val, collections.Iterable):
                        pos_args.append(*received_val)  # prob have to expand given list
                    else:
                        pos_args.append(received_val)  # guess we can't do that, so whatever then, just append it
                elif parameter.kind == parameter.VAR_KEYWORD:
                    if isinstance(received_val, collections.Mapping):
                        kwargs.update(received_val)  # prob have to expand given dict
                    else:
                        kwargs[param_name] = received_val  # can't do, so just set it
                elif parameter.kind == parameter.KEYWORD_ONLY:
                    kwargs[param_name] = received_val

    try:
        return cls(*pos_args, **kwargs)
    except (TypeError, ValueError) as e:
        raise APIJsonParsedTypeMismatchException(f"Unexpected {cls.__qualname__} JSON data received.") from e
    except AttributeError as e:
        raise APIJsonParseException(f"Unexpected {cls.__qualname__} JSON data received.") from e
