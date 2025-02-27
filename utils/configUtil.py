import copy
from typing import Union, Any, Optional
import os
import json
import yaml
import types
import re
from functools import reduce


class UnifyConfig(object):
    """
        Unified config object
    """

    def __init__(self, dic: Optional[dict] = None):
        self.__config__ = dic or dict()

    @classmethod
    def from_py_module(cls, module_object: types.ModuleType):
        return cls(
            {k: (getattr(module_object, k) if not k.endswith("_PATH") else os.path.realpath(getattr(module_object, k)))
             for k in dir(module_object) if k[0].isupper()}
        )
    
    def dot_get(self, dot_string: str, default_value: Any = None, require=False):
        keys = [self.__config__] + dot_string.strip().split('.')
        if not require:
            try:
                return reduce(lambda x, y: x[y], keys)
            except KeyError:
                return default_value
        else:
            return reduce(lambda x, y: x[y], keys)
        
    def dot_set(self, dot_string: str, value: Any = None):
        keys = dot_string.strip().split('.')
        obj = reduce(lambda x, y: x[y], [self.__config__] + keys[:-1])
        obj[keys[-1]] = value
    
    def dump_file(self, filepath: str, encoding: str = 'utf-8'):
        with open(filepath, "w", encoding=encoding) as f:
            json.dump(
                self.__config__, f, indent=4, ensure_ascii=False,
                default=lambda o: o.__config__ if isinstance(o, UnifyConfig) else str(o)
            )
            
    def dump_fmt(self):
        return json.dumps(
            self.__config__, indent=4, ensure_ascii=False,
            default=lambda o: o.__config__ if isinstance(o, UnifyConfig) else str(o)
        )
    
    def __iter__(self):
        for k in self.__config__.keys():
            yield k

    def __getattr__(self, key: str):
        if key in self.__config__.keys():
            return self.__config__[key]
        elif key in dir(self):
            return self.__dict__[key]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __setattr__(self, key: str, value: Any):
        if key != "__config__":
            self.__config__[key] = value
        else:
            self.__dict__[key] = value

    def __delattr__(self, key: str):
        if key in self.__config__.keys():
            del self.__config__[key]
        elif key in dir(self):
            raise AttributeError(f"attribute '{key}' is not allowed to delete")
        else:
            raise AttributeError(f"'{self.__class__.__base__}' object has no attribute '{key}'")

    def __setitem__(self, key: str, value: Any):
        assert key not in dir(self), "conflict with dir(self)"
        self.__config__[key] = value

    def __getitem__(self, key: str):
        return self.__config__[key]

    def __delitem__(self, key: str):
        del self.__config__[key]

    def __str__(self):
        return f"{self.__class__.__name__}({self.__config__})"

    def __repr__(self):
        return self.__str__()

    def __copy__(self):
        cls = self.__class__
        return cls(dic=copy.copy(self.__config__))

    def __deepcopy__(self, memo: Any):
        cls = self.__class__
        return cls(dic=copy.deepcopy(self.__config__, memo=memo))
