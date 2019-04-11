"""Quantum Inspire library

Copyright 2019 QuTech Delft

qilib is available under the [MIT open-source license](https://opensource.org/licenses/MIT):

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import unittest
import numpy as np

from qilib.utils.serialization import serialize, unserialize


class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.testdata = [10, 3.14, 'string', b'bytes', {'a': 1, 'b': 2}, [1, 2], [1, [2, 3]]]
        self.testdata_arrays = [np.array([1, 2, 3]), np.array([1.0, 2.0]), np.array([[1.0, 0], [0, -.2], [0.123, .0]])]

    def test_serialization_default_types(self):
        for x in self.testdata:
            s = serialize(x)
            xx = unserialize(s)
            self.assertEqual(x, xx)
        for x in self.testdata_arrays:
            s = serialize(x)
            xx = unserialize(s)
            self.assertSequenceEqual(x.tolist(), xx.tolist())

    def test_non_serializable_objects(self):
        with self.assertRaisesRegex(TypeError, 'is not JSON serializable'):
            serialize(object())