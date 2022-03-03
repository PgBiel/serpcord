__all__ = ("_init_model_from_mapping_json_data", "parse_json_response", "parse_json_list_response")

import datetime
import json
import typing
import types
import inspect
import collections
import collections.abc

import aiohttp

from serpcord.exceptions import APIJsonParsedTypeMismatchException, APIJsonParseException, APIDataParseException
from serpcord.models.model_abc import JsonAPIModel
from typing import Optional, TypeVar, Mapping, Any, Type, Dict, Callable, List, Iterable, Union, Tuple

T = TypeVar("T", bound=JsonAPIModel[Mapping[str, Any]])
D = TypeVar("D")
V = TypeVar("V")

if typing.TYPE_CHECKING:
    from serpcord.botclient import BotClient


def _get_annotation_port(obj, *, globals=None, locals=None, eval_str=False, merge_globals_locals=False):
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
    elif merge_globals_locals:  # NOTE: I changed the port code to include merging of globals/locals.
        if isinstance(obj_globals, collections.abc.Mapping):
            globals = {**obj_globals, **globals}

    if locals is None:
        locals = obj_locals
    elif merge_globals_locals:
        if isinstance(obj_locals, collections.abc.Mapping):
            locals = {**obj_locals, **locals}

    return_value = {key:
        value if not isinstance(value, str) else eval(value, globals, locals)
        for key, value in ann.items() }
    return return_value


# if hasattr(typing, "Literal"):
#     LiteralTrue = typing.Literal[True]
#     LiteralFalse = typing.Literal[False]
# else:
#     LiteralTrue = LiteralFalse = bool


# _GenericAlias = typing.cast(Any, getattr(typing, "_GenericAlias", type))

def _typing_generic_converter(T: Any, *, recursive: bool = True) -> Union[type, Tuple[Any, ...]]:
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
        Union[:class:`type`, Tuple[Any, ...]]: The simplified type(s). If the given type was not
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


if hasattr(typing, "get_origin"):
    _typing_get_origin = typing.get_origin
else:
    def _typing_get_origin(tp):
        """Get the unsubscripted version of a type.

        This supports generic types, Callable, Tuple, Union, Literal, Final, ClassVar
        and Annotated. Return None for unsupported types. Examples::

            get_origin(Literal[42]) is Literal
            get_origin(int) is None
            get_origin(ClassVar[int]) is ClassVar
            get_origin(Generic) is Generic
            get_origin(Generic[T]) is Generic
            get_origin(Union[T, int]) is Union
            get_origin(List[Tuple[T, T]][int]) == list
        """
        _AnnotatedAlias = getattr(tp, "_AnnotatedAlias", None)
        _BaseGenericAlias = getattr(tp, "_BaseGenericAlias", None)
        GenericAlias = getattr(types, "GenericAlias", None)  # py 3.9+
        if isinstance(_AnnotatedAlias, type) and isinstance(tp, _AnnotatedAlias):
            return typing.Annotated
        if (
            ((isinstance(_BaseGenericAlias, type) and isinstance(tp, _BaseGenericAlias))
                or (isinstance(GenericAlias, type) and isinstance(tp, GenericAlias)))
            and hasattr(tp, "__origin__")
        ):
            return tp.__origin__
        if tp is typing.Generic:
            return typing.Generic
        return None

if hasattr(typing, "get_args"):
    _typing_get_args = typing.get_args
else:
    def _typing_get_args(tp) -> tuple:
        """Gets the inner parameter(s) of a generic annotation. Returns empty tuple if not a generic annotation
        type. I.e., ``_typing_get_arg(C[T]) == (T,)``, while ``_typing_get_arg(T) == ()``
        (assuming ``T`` isn't a generic annotation).

        Args:
            tp: The generic alias whose parameters should be extracted.

        Returns:
            :class:`tuple`: The parameter(s).

        Examples:
            .. testsetup::

                from serpcord.utils.model import _typing_get_args
            .. doctest

                >>> from typing import List, Union
                >>> _typing_get_args(List[str])
                (<class 'str'>,)
                >>> _typing_get_args(Union[str, int, bool])
                (<class 'str'>, <class 'int'>, <class 'bool'>)
                >>> _typing_get_args(str)
                ()
        """
        if hasattr(tp, "__origin__"):
            if hasattr(tp, "__metadata__"):
                return (tp.__origin__,) + tp.__metadata__
            if hasattr(tp, "__args__"):
                res = tp.__args__
                if tp.__origin__ is collections.abc.Callable and res[0] is not Ellipsis:
                    res = (list(res[:-1]), res[-1])
                return res
        return ()


def _safe_issubclass(type_a: Any, type_b: Union[Any, Tuple[Any]]) -> bool:
    """Similar to :func:`issubclass`, however suppresses the TypeError when a parameter isn't a class.
    Useful for annotations which we don't know whether they are actual types or simply strings which can't be compared.
    
    Args:
        type_a (Any): Type A (subclass).
        type_b (Union[Any, Tuple[Any, ...]]): Type B (parent class, or possible parent classes).

    Returns:
        :class:`bool`: ``True`` if ``type_a`` is a subclass of ``type_b``; ``False`` otherwise, or if one of them isn't
        a type.
    """
    try:
        return issubclass(type_a, type_b)
    except TypeError:
        return False


def _safe_index(obj: Any, index: Any, *, default: D = None) -> Union[Any, D]:
    """Similar to ``obj[index]``, however suppresses the TypeError if ``obj`` doesn't support this operation.

    Args:
        obj (Any): Object to be indexed with `index`.
        index (Any): Index to retrieve from `obj`.
        default (``D``, optional): A value to serve as default, if indexing fails (defaults to ``None``)

    Returns:
        Union[Any, ``D``]: Returns ``obj[index]``, or ``default`` if a :exc:`TypeError` is raised.
    """
    try:
        return obj[index]
    except TypeError:
        return default


def _parse_datetime_from_json_iso_str(datestr: str) -> datetime.datetime:
    """Parses a ISO8601 string obtained through the Discord API into a :class:`datetime.datetime` object.

    Args:
        datestr (:class:`str`): The ISO8601 to be parsed.

    Returns:
        :class:`datetime.datetime`: The resulting datetime object.

    Raises:
        :exc:`APIJsonParseException`: If the string supplied wasn't a valid ISO8601-compliant date string.
    """
    try:
        return datetime.datetime.fromisoformat(datestr)
    except (TypeError, ValueError) as e:
        raise APIJsonParseException("Invalid ISO8601 datetime received.") from e


def _default_converters(value: V,
                        *, client: "BotClient",
                        annotated_type: Any, raise_not_implemented: bool = False) -> Union[Any, V]:
    """Converts a value received through a JSON endpoint in the Discord API to expected types in a model's init
    parameters (refer to :func:`init_model_from_mapping_json_data`.

    Args:
        value (``V``): Value to convert.
        client (:class:`~.BotClient`): The bot's active client instance.
        annotated_type (Any): The expected type annotation for the value. (Conversion should turn the value into
            said type, if possible.)
        raise_not_implemented (:class:`bool`, optional): If ``True``, raises :exc:`NotImplementedError` instead of
            returning the given value if none of the default converters were of use. (Defaults to ``False``)

    Returns:
        Union[Any, ``V``]: The converted value, or ``value`` if none of the default type converters were of use.
    """
    converted_type = _typing_generic_converter(annotated_type)  # reduce C[T] to C; Union[A, B, ...]
    first_generic_index = _safe_index(_typing_get_args(annotated_type), 0)  # C[T] -> T
    second_generic_index = _safe_index(_typing_get_args(annotated_type), 1)  # C[K, V] -> V
    if (  # parse dicts of JsonAPIModel s
        _safe_issubclass(converted_type, typing.Mapping)
        and isinstance(second_generic_index, type)
        and issubclass(second_generic_index, JsonAPIModel)
        and isinstance(value, collections.abc.Mapping)
    ):  # Mapping[str, JsonAPIModel] or subclasses  => need to parse dict values into JsonAPIModel
        return {k_: second_generic_index._from_json_data(client, v_) for k_, v_ in value.items()}
    elif (  # parse lists of JsonAPIModel s
        _safe_issubclass(converted_type, typing.Iterable)
        and not _safe_issubclass(converted_type, str)
        and isinstance(first_generic_index, type)
        and issubclass(first_generic_index, JsonAPIModel)
        and isinstance(value, collections.abc.Iterable)
    ):  # Iterable[JsonAPIModel]  => need to parse list values into JsonAPIModel
        return [first_generic_index._from_json_data(client, x) for x in value]
    elif (  # parse ISO8601 date string
        _safe_issubclass(converted_type, datetime.datetime)
        and isinstance(value, str)
    ):
        return _parse_datetime_from_json_iso_str(value)
    elif (  # parameter type is not a Union - it's a single type -, so just run a simple isinstance
        isinstance(converted_type, type)  # check to then proceed to convert to the relevant JSON Model,
        and issubclass(converted_type, JsonAPIModel)  # if necessary (This isn't exactly a typecheck
        and not isinstance(value, converted_type)  # - it just converts raw data to JsonAPIModel
    ):                                                 # when a subclass of it is expected.)
        return converted_type._from_json_data(client, value)
    else:  # not JsonAPIModel, not a list or dict of JSON Models, not datetime, so no default converters for this
        if raise_not_implemented:  # used to differentiate from other kinds of errors, if needed
            raise NotImplementedError(
                f"No default converter found to parse {type(value).__qualname__} into {annotated_type!r}."
            )
        return value


# inject (Optional[Mapping[:class:`str`, Mapping[:class:`str`, Any]]]): If specified, this dictionary maps
#  post-rename received JSON keys (according to the given ``rename`` dict) to a dict that should be merged
#  to the received dict for that parameter (if a dict was received for that key - otherwise no-op). (Defaults
#  to ``None``, meaning no injection occurs.)
#
#  For example, a :class:``
#  The `inject` parameter for :class:`~.Guild` would then look something like this::
#
#      _init_model_from_mapping_json_data(..., inject={"members": {"guild": } } )

def _init_model_from_mapping_json_data(cls: Type[T], client: "BotClient", json_data: Mapping[str, Any], *,
                                       rename: Optional[Mapping[str, str]] = None,
                                       type_check_types: Union[bool, Iterable[Any]] = False,
                                       type_check_except: Optional[Iterable[Any]] = None,
                                       converters: Optional[Mapping[str, typing.Callable[[Any], Any]]] = None,
                                       extra_globals: Optional[Mapping[str, Any]] = None,
                                       extra_locals: Optional[Mapping[str, Any]] = None) -> T:
    """Generic function for instantiating :class:`~.JsonAPIModel` subclasses
    from given JSON :class:`dict` (Mapping) data. Works by taking keys from the received JSON data and passing them as
    parameters to the model's ``__init__`` function, with additional checks along the way.

    Args:
        cls (Type[``T``]): The class of the model that should be instantiated, hereby represented by ``T``.
        client (:class:`~.BotClient`): The bot's active client instance.
        json_data (Mapping[:class:`str`, Any]): The JSON data to convert to a model instance (a Mapping/:class:`dict`).
        rename (Optional[Mapping[:class:`str`, :class:`str`]], optional): A Mapping/:class:`dict` to map keys received
            from the API to valid init parameter names. (Defaults to ``None`` - no additional mapping is
            done, and only ``json_data`` keys that are also valid ``cls.__init__`` parameters will be considered - other
            keys will be ignored.)
        converters (Optional[Mapping[:class:`str`, Callable[[Any], Any]]]): Custom converters for init parameters, if
            needed. A mapping with keys being the post-rename received JSON keys (according to the given ``rename``
            dict) and their respective values being a function that maps the received parsed JSON value into an object
            the init can accept. For example, mapping a list of objects into a list of a model by parsing each object
            in a custom way, for a specific parameter. (Defaults to ``None`` - only default converters - such as
            :meth:`JsonAPIModel._from_json_data` - are used.)
        type_check_types (Union[:class:`bool`, Iterable[:class:`type`]], optional): An optional list of type annotations
            for which type checks should be run, or ``True`` to run type checks for all parameter types.
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
        type_check_except (Optional[Iterable[:class:`type`]]): An optional list of type annotations that should be
            excluded from type checks. Useful if ``type_check_types=True`` is specified, but some should be excluded
            due to receiving special treatment (say, due to a special converter). Defaults to ``None`` (only the
            ``type_check_types`` is considered for type checks by default).
        extra_globals (Optional[Mapping[:class:`str`, Any]), optional): Extra global vars to consider when parsing
            ``cls.__init__`` 's annotations (if one or more are strings). Note that :class:`~.BotClient` is included
            by default. (Defaults to ``None``, meaning no extra global variables - other than :class:`~.BotClient` -
            will be included for the annotation type parsing.)
        extra_locals (Optional[Mapping[:class:`str`, Any]], optional): Extra local vars to consider when parsing
            ``cls.__init__`` 's annotations (if one or more are strings). (Defaults to ``None``, meaning no extra local
            variables will be included for the annotation type parsing.)

    Returns:
        ``T``: The constructed model (instance of ``cls``, constructed through ``cls.__init__``).

    Raises:
        :exc:`APIJsonParseException`: If the given ``json_data`` had unexpected parameter values/types.

    Examples:
        .. testsetup:: *

            from serpcord.utils.model import init_model_from_mapping_json_data
            token = "123"
        .. doctest::

            >>> from serpcord import BotClient, PermissionOverwrite
            >>> bot = BotClient(token)
            >>> json_data = { "id": 123, "type": 1, "allow": 0, "deny": 1048580 }
            >>> PermissionOverwrite._from_json_data(bot,json_data)
            PermissionOverwrite(target_id=Snowflake(value=123), overwrite_type=<PermissionOverwriteType.MEMBER: 1>, \
allow=<PermissionFlags.NONE: 0>, deny=<PermissionFlags.CONNECT|BAN_MEMBERS: 1048580>)
    """
    from serpcord.botclient import BotClient  # lazy import to avoid cyclic import
    actual_extra_globals: Dict[str, Any] = {**(extra_globals or dict()), "BotClient": BotClient}

    if not isinstance(cls, type):
        raise TypeError("'cls' must be a class.")

    if not isinstance(json_data, collections.abc.Mapping):
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
    annotations: Dict[str, Any] = _get_annotation_port(
        init_method, eval_str=True, globals=actual_extra_globals, locals=extra_locals, merge_globals_locals=True
    )

    # key/values given through json_data (and parsed/renamed)
    received_params: Dict[str, Any] = dict()

    type_check_types_tuple = tuple(
        type_check_types
    ) if isinstance(type_check_types, collections.abc.Iterable) else tuple()
    type_check_except_tuple = tuple(
        type_check_except
    ) if isinstance(type_check_except, collections.abc.Iterable) else tuple()

    full_receiving_data = {
        **json_data,
        "client": client  # setting client in case it is necessary (if cls.__init__ requires client as param)
    }
    gen_alias = getattr(typing, "_GenericAlias")  # <- type for objects of form C[T], where C and T are types
    for k, v in full_receiving_data.items():
        renamed = rename.get(k, k) if rename is not None else k  # rename according to map
        if accepts_kwargs or renamed in expected_keys:  # is valid param name (or **kwargs is present => any name's OK)
            possible_json_model = annotations.get(renamed, None)  # get the param's type annotation (a possible
            converted_type: Optional[Union[type, Tuple[type, ...]]] = None         # JSON model to be parsed from data)
            # possible_json_models: List[Type[JsonAPIModel]] = []
            set_value: Any = v  # post-JSON model parsing value
            pjm_is_type_or_gen_alias = False  # True if possible_json_model is a type or Generic alias (C or C[T])
            custom_converter = converters.get(renamed, None) if converters is not None else None
            custom_converting = False
            if callable(custom_converter):  # a custom converter was specified for this parameter
                set_value = custom_converter(v)
                custom_converting = True
            if (  # check if possible_json_model is a type, and later if they're a JsonAPIModel, for conversions and
                isinstance(possible_json_model, type)  # form C                                # type checking.
                or (isinstance(gen_alias, type) and isinstance(possible_json_model, gen_alias))  # form C[T]
            ):
                pjm_is_type_or_gen_alias = True
                converted_type = _typing_generic_converter(possible_json_model)  # reduce C[T] to C; Union[A, B, ...]
                converted_type_non_recursive = _typing_generic_converter(possible_json_model, recursive=False)
                last_error: Optional[Exception] = None                           # to (A, B, ...); Optional[T] to T
                if not custom_converting:  # run default conversions
                    if isinstance(converted_type_non_recursive, tuple):  # 2+ possibilities for param (Union[A,B,...])
                        has_non_jsonapimodel: bool = False
                        for possible_type in converted_type_non_recursive:  # -> go thru each possible type & attempt to
                            converted_subtype = _typing_generic_converter(possible_type)  # use default parsing methods
                            try:
                                set_value = _default_converters(
                                    v, client=client, annotated_type=possible_type,
                                    raise_not_implemented=True
                                )
                                break
                            except NotImplementedError:  # no default converters were applied for the given type
                                pass  # so just keep going to see if there's still something we can do
                            except (APIDataParseException, TypeError) as e:
                                last_error = e  # tried to parse into a JsonAPIModel but couldn't
                                continue
                            if isinstance(converted_subtype, type):  # other type parsing stuff
                                if isinstance(v, converted_subtype):
                                    break  # done, v already has a compatible type.
                                elif not issubclass(converted_subtype, JsonAPIModel):
                                    # -> since a Non-JsonAPIModel type is possible, don't error for mismatched type
                                    # if we aren't able to convert at all to avoid needless type-checking, since
                                    # Non-JsonAPIModel type checking is done later with
                                    # the type_check_types parameter.
                                    has_non_jsonapimodel = True

                        else:  # JSON data received did not fit into any of the possible types.
                            if not has_non_jsonapimodel:  # all are jsonapimodels and all conversion attempts failed
                                json_error = APIJsonParseException(  # -> raise
                                    f"Unexpected {cls.__qualname__} JSON data received. \
    (Key: {repr(k)}; Received: {repr(v)}, of type {type(v).__qualname__}; Failed to parse to {repr(possible_json_model)})"
                                )
                                if last_error is not None and isinstance(last_error, Exception):
                                    raise json_error from last_error  # get last parse failure to show why op failed
                                else:
                                    raise json_error
                    else:
                        set_value = _default_converters(v, client=client, annotated_type=possible_json_model)

            if (  # begin typechecking.
                pjm_is_type_or_gen_alias
                and converted_type is not None
                and possible_json_model not in type_check_except_tuple
                and (
                    type_check_types is True  # check all types... or just this one
                    or possible_json_model in type_check_types_tuple
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
                    if isinstance(v, collections.abc.Mapping):
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
                    if isinstance(received_val, collections.abc.Iterable):
                        pos_args.append(*received_val)  # prob have to expand given list
                    else:
                        pos_args.append(received_val)  # guess we can't do that, so whatever then, just append it
                elif parameter.kind == parameter.VAR_KEYWORD:
                    if isinstance(received_val, collections.abc.Mapping):
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


async def parse_json_response(response: aiohttp.ClientResponse) -> typing.Any:
    """Helper function for parsing a generic JSON response, using :mod:`json`.

    Args:
        response (:class:`aiohttp.ClientResponse`): The response object from which the JSON data should be extracted.

    Returns:
        Any: The parsed JSON data (using :func:`json.loads`). (May be any primitive type.)

    Raises:
        :exc:`APIJsonParseException`: If the JSON data received was invalid (or no such data was received).
    """
    try:
        return await response.json()
    except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
        raise APIJsonParseException("Malformed/non-JSON data received.") from e


TJsonAPIModel = typing.TypeVar("TJsonAPIModel", bound=JsonAPIModel)
async def parse_json_list_response(
    cls: Type[TJsonAPIModel], client: "BotClient", response: aiohttp.ClientResponse
) -> List[TJsonAPIModel]:
    """Helper function for parsing received JSON data into a list of instances of a certain :class:`~.JsonAPIModel`
    subclass.

    Args:
        cls (Type[``TJsonAPIModel``]): The class of the desired model (must subclass :class:`~.JsonAPIModel`).
        client (:class:`~.BotClient`): The bot's active client instance.
        response (:class:`aiohttp.ClientResponse`): The response object from which the JSON data should be extracted.

    Returns:
        List[``TJsonAPIModel``]: List of instances of `cls` parsed from the received JSON data (if it is a list of
        valid `cls` data).

    Raises:
        :exc:`APIJsonParseException`: If the JSON data received was invalid (or no such data was received).
        :exc:`APIJsonParsedTypeMismatchException`: If the JSON data received was not a list.
    """
    resp = await parse_json_response(response)
    if not isinstance(resp, collections.abc.Iterable):
        raise APIJsonParsedTypeMismatchException("JSON received wasn't a list.")
    return [cls._from_json_data(client, x) for x in resp]
