import numpy as np


class PythonJsonStructure(dict):

    __serializable_container_types = (list, tuple, np.ndarray)
    __serializable_value_types = (type(None), bool, int, float, complex, str, bytes)

    def __init__(self, *args, **kwargs):
        """ A python container which can hold data objects and can be serialized
            into JSON. Currently the following data types can be added to the
            container object: bool, bytes, int, float, list, tuple, dict
            PythonJsonStructure and numpy arrays. The PythonJsonStructure is a
            dictionary with similar calling methods, but with some
            limitations/restrictions.

        Args:
            *args: A serializable dictionary with key value pair data.
            **kwargs: Arbitrary keyword arguments with serializable values.
        """
        super().__init__()
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        """ Appends or changes an item of the container.

        Args:
            key (str): The key of the container item.
            value (a supported data-type): The value of the updated item.
        """

        PythonJsonStructure.__assert_correct_key_type(key)
        super().__setitem__(key, self.__check_serializability(value))

    def update(self, *args, **kwargs):
        """ Update the PythonJsonStructure with the key/value pairs from other
            dict/PythonJsonStructure, overwriting existing keys."""
        if args:
            args_data = args[0]
            for key, value in args_data.items():
                self[key] = value
        if kwargs:
            kwargs_items = kwargs.items()
            for key, value in kwargs_items:
                self[key] = value

    def setdefault(self, key, default=None):
        """ If key is in the dictionary, return its value. If not, insert key
            with a value of default and return default.

        Args:
            key (str): The key of the container item.
            default (any): The default value of the updated item.
        """
        PythonJsonStructure.__assert_correct_key_type(key)
        return super().setdefault(key, self.__check_serializability(default))

    def __check_serializability(self, data):
        if PythonJsonStructure.__is_value_type(data):
            return data

        if PythonJsonStructure.__is_dict_type(data):
            return PythonJsonStructure(data)

        if PythonJsonStructure.__is_container_type(data):
            if isinstance(data, list):
                return [self.__check_serializability(item) for item in data]

            if isinstance(data, tuple):
                return tuple([self.__check_serializability(item) for item in data])

            if isinstance(data, np.ndarray):
                return self.__check_serializability_ndarray(data)

        raise TypeError('Data is not serializable ({})!'.format(type(data)))

    @staticmethod
    def __assert_correct_key_type(key):
        if not isinstance(key, str):
            raise TypeError('Invalid key! (key={})'.format(key))

    @staticmethod
    def __is_value_type(value):
        return isinstance(value, PythonJsonStructure.__serializable_value_types)

    @staticmethod
    def __is_dict_type(data):
        return isinstance(data, (PythonJsonStructure, dict))

    @staticmethod
    def __is_container_type(data):
        return isinstance(data, PythonJsonStructure.__serializable_container_types)

    def __check_serializability_ndarray(self, data):
        return_data = np.empty_like(data)
        for index in np.ndindex(data.shape):
            return_data[index] = self.__check_serializability(data[index])
        return return_data