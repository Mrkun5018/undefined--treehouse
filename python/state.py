import os
import json
import requests
from typing import Optional, Any, Dict


def generate_variable_names(data, prefix: Optional[str] = None, debug=False) -> Dict[str, Any]:
    """
    Generate variable names for a given data structure.

    Args:
        data: The data structure to generate variable names for.
        prefix: The prefix to use for the variable names.
        debug: Whether to print the variable names.

    Returns:
        A dictionary of variable names and their corresponding values.
    """
    names = {}
    for key, value in data.items():
        if isinstance(value, dict):
            generate_variable_names(value, prefix=key if prefix is None else f"{prefix}_{key}")
        else:
            if prefix is not None:
                if len(key) == 0:
                    key = prefix
                else:
                    key = f"{prefix}_{key}"

            if debug:
                if isinstance(value, str):
                    print(f"{key} = '{value}'")
                else:
                    print(f"{key} = {value}")
            names[key] = value
    return names


class state:
    """
    A class to manage state.
    This class is used to load and save state from and to a file or remote location.
    It also provides methods to update the state.
    """
    __filepath = None

    @classmethod
    def load_from_locally(cls, filepath: Optional[str] = None):
        """
        Load state from a file.

        Args:
            filepath: The filepath to load from.
        """
        if filepath is None:
            filepath = cls.__filepath

        if filepath is None:
            raise ValueError("No filepath provided")

        if not os.path.exists(filepath):
            return cls.save_to_locally(filepath)

        with open(filepath, 'r', encoding="utf-8") as f:
            cls._mapping_attribute(json.load(f))

    @classmethod
    def load_from_remotely(cls, url):
        """
        Load state from a remote location.

        Args:
            url: The URL to load from.
        """
        response = requests.get(url)
        cls._mapping_attribute(response.json())

    @classmethod
    def save_to_locally(cls, filepath: Optional[str] = None):
        """
        Save state to a file.

        Args:
            filepath: The filepath to save to.
        """
        filepath = filepath or cls.__filepath
        with open(filepath, 'w', encoding="utf-8") as f:
            json.dump(cls.dict(), f)

    @classmethod
    def save_to_remotely(cls, url):
        """
        Save state to a remote location.

        Args:
            url: The URL to save to.
        """
        response = requests.post(url, json=cls.dict())
        return response.status_code == 200

    @classmethod
    def _mapping_attribute(cls, data):
        """
        Map the attributes of the class to the data.

        Args:
            data: The data to map to the class.
        """
        variable_names = generate_variable_names(data)
        for variable, value in variable_names.items():
            if not hasattr(cls, variable):
                raise ValueError(f"{variable} is not a valid attribute")
            setattr(cls, variable, value)

    @classmethod
    def update(cls, key, value):
        """
        Update the state of the class.

        Args:
            key: The key of the state to update.
            value: The value to update the state with.
        """
        if not hasattr(cls, key):
            raise KeyError(f"{key} is not a valid attribute")
        cls.save_to_locally()
        setattr(cls, key, value)

    @classmethod
    def dict(cls):
        """
        Get the state of the class as a dictionary.

        Returns:
            A dictionary of the state of the class.
        """
        return {attr: getattr(cls, attr) for attr in cls.keys()}

    @classmethod
    def keys(cls):
        """
        Get the keys of the state of the class.

        Returns:
            A list of the keys of the state of the class.
        """
        variables = filter(lambda x: not callable(getattr(cls, x)), vars(cls))
        return [attr for attr in variables if not attr.startswith('__')]

    @classmethod
    def values(cls):
        """
        Get the values of the state of the class.

        Returns:
            A list of the values of the state of the class.
        """
        return [getattr(cls, key) for key in cls.keys()]
