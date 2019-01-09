import datetime
from unittest import TestCase

import numpy as np
from qilib.data_set import DataSet, DataArray


class TestDataSet(TestCase):
    def setUp(self):
        self.x_points = np.array(range(0, 10))
        self.y_points = np.array(range(0, 5))
        self.set_x = DataArray(name='x', label='x-axis', unit='mV', is_setpoint=True,
                               preset_data=np.array(self.x_points))
        self.set_y = DataArray(name='y', label='y-axis', unit='mV', is_setpoint=True,
                               set_arrays=(self.set_x,),
                               preset_data=np.tile(np.array(self.y_points), [self.set_x.size, 1]))
        self.data_array = DataArray(name='Z', label='z-axis', unit='ma', set_arrays=[self.set_y, self.set_x],
                                    preset_data=np.NaN * np.ones((self.x_points.size, self.y_points.size)))

    def test_constructor(self):
        storage = 'Fake'
        name = 'ItsAName'
        array_name = 'ItsAnArray'
        time_stamp = datetime.datetime(2018, 12, 24, 18, 0)
        user_data = {'some': 'data'}
        set_arrays = DataArray('setpoints', 'X', is_setpoint=True, preset_data=np.array([1, 2, 3, 4, 5]))
        data_arrays = DataArray(array_name, 'results', shape=(5,), set_arrays=[set_arrays])
        data_set = DataSet(storage=storage, name=name, time_stamp=time_stamp, user_data=user_data,
                           data_arrays=data_arrays, set_arrays=set_arrays)
        self.assertEqual(storage, data_set.storage)
        self.assertEqual(name, data_set.name)
        self.assertEqual(time_stamp, data_set.time_stamp)
        self.assertDictEqual(user_data, data_set.user_data)
        self.assertEqual(data_arrays, data_set.data_arrays[array_name])
        self.assertEqual(array_name, data_set.default_array_name)

    def test_constructor_multiple_set_arrays(self):
        storage = 'Fake'
        name = 'ItsAName'
        array_name = self.data_array.name
        user_data = {'some': 'data'}
        data_set = DataSet(storage=storage, name=name, user_data=user_data,
                           data_arrays=self.data_array, set_arrays=[self.set_y, self.set_x])
        self.assertEqual(storage, data_set.storage)
        self.assertEqual(name, data_set.name)
        self.assertDictEqual(user_data, data_set.user_data)
        self.assertEqual(self.data_array, data_set.data_arrays[array_name])
        self.assertEqual(array_name, data_set.default_array_name)

    def test_constructor_multiple_data_arrays(self):
        storage = 'Fake'
        name = 'ItsAName'
        array_name = 'ItsAnArray'
        user_data = {'some': 'data'}

        x_points = np.array(range(0, 10))
        y_points = np.array(range(0, 5))
        x = DataArray(name='x', label='x-axis', unit='mV', is_setpoint=True,
                      preset_data=np.array(x_points))
        y = DataArray(name='y', label='y-axis', unit='mV', is_setpoint=True,
                      set_arrays=(x,), preset_data=np.tile(np.array(y_points), [x.size, 1]))
        z = DataArray(name=array_name, label='z-axis', unit='ma', set_arrays=[y, x],
                      preset_data=np.NaN * np.ones((x_points.size, y_points.size)))
        other_z = DataArray(name='other_array', label='z-axis', unit='ma', set_arrays=[y, x],
                            preset_data=np.NaN * np.ones((x_points.size, y_points.size)))

        data_set = DataSet(storage=storage, name=name, user_data=user_data,
                           data_arrays=[z, other_z], set_arrays=[y, x])
        self.assertEqual(storage, data_set.storage)
        self.assertEqual(name, data_set.name)
        self.assertDictEqual(user_data, data_set.user_data)
        self.assertEqual(z, data_set.data_arrays[array_name])
        self.assertEqual(array_name, data_set.default_array_name)

        with self.assertRaises(TypeError) as error:
            DataSet(data_arrays=np.array([1, 2, 3, 4]))
        self.assertIn("'data_arrays' have to be of type 'DataArray', not <class 'numpy.ndarray'>", error.exception.args)

    def test__repr__(self):
        data_set = DataSet(name='some_name', time_stamp=datetime.datetime(2000, 1, 1), user_data={'user': 'data'},
                           set_arrays=[])
        expect = "DataSet(id={}, name='{}', storage=None, time_stamp={}, user_data={}, data_arrays={}, set_arrays={})" \
            .format(id(data_set), 'some_name', 'datetime.datetime(2000, 1, 1, 0, 0)', {'user': 'data'}, {}, [])
        self.assertEqual(expect, repr(data_set))

    def test_add_array(self):
        array_name = 'some_array'
        data_array = DataArray(array_name, 'label', preset_data=np.array([1, 2, 3, 4, 5]))
        data_set = DataSet()
        data_set.add_array(data_array)
        self.assertListEqual(list(data_array), list(data_set.some_array))
        self.assertListEqual(list(data_array), list(data_set.data_arrays[array_name]))
        self.assertIs(data_set.some_array, data_set.data_arrays[array_name])

    def test_add_array_duplicate_raises_error(self):
        name = 'some_array'
        data_array = DataArray(name, 'label', preset_data=np.array([1, 2, 3, 4, 5]))
        data_set = DataSet()
        data_set.add_array(data_array)
        with self.assertRaises(ValueError) as error:
            data_set.add_array(data_array)
        self.assertEqual(("DataSet already contains an array with the name '{}'".format(name),), error.exception.args)

    def test_add_array_with_bad_name(self):
        data_array = DataArray('this is not a good name', 'label', preset_data=np.array([1, 2, 3, 4, 5]))
        data_set = DataSet()
        with self.assertRaisesRegex(SyntaxError, "'this is not a good name' is an invalid name for an identifier."):
            data_set.add_array(data_array)
        data_array.name = 99
        with self.assertRaisesRegex(ValueError, "Array name has to be string, not <class 'int'>"):
            data_set.add_array(data_array)

    def test_add_array_set_arrays_mismatch(self):
        some_points = DataArray('some_points', 'label', is_setpoint=True, preset_data=np.array([1, 2, 3, 4, 5]))
        some_array = DataArray('some_array', 'label', set_arrays=[some_points], shape=(5,))
        other_points = DataArray('other_points', 'label', is_setpoint=True, preset_data=np.array([1, 2, 3, 4, 5]))
        other_array = DataArray('other_array', 'label', set_arrays=[other_points], shape=(5,))
        data_set = DataSet()
        data_set.add_array(some_array)
        with self.assertRaises(ValueError) as error:
            data_set.add_array(other_array)
        self.assertEqual(("Set point arrays do not match.",), error.exception.args)

    def test_add_data(self):
        some_array = DataArray('some_array', 'label', shape=(5, 5))
        data_set = DataSet(data_arrays=some_array)

        data_set.add_data((4, 4), {'some_array': 42})
        self.assertEqual(42, some_array[4][4])

        data_set.add_data(3, {'some_array': [1, 2, 3, 4, 5]})
        self.assertListEqual([1, 2, 3, 4, 5], list(some_array[3]))

    def test_add_data_higher_dimensions(self):
        some_array = DataArray('some_array', 'label', shape=(5, 5, 5, 5))
        data_set = DataSet(data_arrays=some_array)

        data_set.add_data((3, 3, 3, 3), {'some_array': 0.42})
        self.assertEqual(0.42, some_array[3][3][3][3])

        double_array = [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]
        data_set.add_data((2, 2), {'some_array': double_array})
        self.assertTrue(np.array_equal(double_array, some_array[2][2]))
        self.assertFalse(np.array_equal(double_array, some_array[2][1]))

    def test_setters(self):
        data_set = DataSet()
        self.assertEqual('', data_set.name)
        self.assertIsInstance(data_set.time_stamp, datetime.datetime)
        self.assertIsNone(data_set.user_data)
        self.assertEqual("", data_set.default_array_name)

        data_set.name = 'TheName'
        data_set.time_stamp = datetime.datetime(2018, 12, 24, 18)
        data_set.user_data = {'Data': 'stuff'}
        data_set.default_array_name = 'TheDefault'

        self.assertEqual('TheName', data_set.name)
        self.assertEqual(datetime.datetime(2018, 12, 24, 18), data_set.time_stamp)
        self.assertDictEqual({'Data': 'stuff'}, data_set.user_data)
        self.assertEqual("TheDefault", data_set.default_array_name)

    def test_sync_from_storage(self):
        data_set = DataSet()
        self.assertRaisesRegex(NotImplementedError, "sync_from_storage has not been implemented.",
                               data_set.sync_from_storage)

    def test_save_to_storage(self):
        data_set = DataSet()
        self.assertRaisesRegex(NotImplementedError, "save_to_storage has not been implemented.",
                               data_set.save_to_storage)

    def test_finalize(self):
        data_set = DataSet()
        self.assertRaisesRegex(NotImplementedError, "finalize has not been implemented.", data_set.finalize)

    def test_string(self):
        storage = 'Fake'
        name = 'ItsAName'
        array_name = 'ItsAnArray'
        user_data = {'some': 'data'}

        x_points = np.array(range(0, 10))
        y_points = np.array(range(0, 5))
        x = DataArray(name='x', label='x-axis', unit='mV', is_setpoint=True,
                      preset_data=np.array(x_points))
        y = DataArray(name='y', label='y-axis', unit='mV', is_setpoint=True,
                      set_arrays=(x,), preset_data=np.tile(np.array(y_points), [x.size, 1]))
        z = DataArray(name=array_name, label='z-axis', unit='ma', set_arrays=[y, x],
                      preset_data=np.NaN * np.ones((x_points.size, y_points.size)))
        other_z = DataArray(name='other_array', label='z-axis', unit='ma', set_arrays=[y, x],
                            preset_data=np.NaN * np.ones((x_points.size, y_points.size)))

        data_set = DataSet(storage=storage, name=name, user_data=user_data,
                           data_arrays=[z, other_z], set_arrays=[y, x])

        expected = "DataSet: ItsAName\n  name        | label  | unit | shape   | setpoint\n  ItsAnArray  | z-axis | " \
                   "ma   | (10, 5) | False\n  other_array | z-axis | ma   | (10, 5) | False\n  y           | y-axis |" \
                   " mV   | (10, 5) | True\n  x           | x-axis | mV   | (10,)   | True"
        actual = str(data_set)
        self.assertEqual(expected, actual)
