from collections import namedtuple
from ..service import shape, ShapeNode, node_graph_to_obj, DictShape, ListShape, TupleShape
from types import SimpleNamespace
from .base_test import get_civitai_sample
import json
from bs4 import BeautifulSoup

def test_shape_node():
    main = ShapeNode({})
    foo = main.add_child(ShapeNode(container_type="foo"))
    foo.add_child(ShapeNode(value="str"))
    r = node_graph_to_obj(main)
    assert r == {"foo": "str"}

def test_shape_node2():
    main = ShapeNode({})
    foo = main.add_child(ShapeNode(container_type="foo"))
    foo.add_child(ShapeNode(value="str"))
    foo.add_child(ShapeNode(value="int"))
    r = node_graph_to_obj(main)
    assert r == {"foo": "str|int"}

def test_eval_shape_prim():
    assert shape(1) == 'int'

def test_eval_shape_list_empty():
    assert shape([]) == []

def test_eval_shape_list():
    assert shape([1, 2, 2, 2]) == ['int']

def test_eval_shape_list1():
    assert shape([1, 2, 2.0, 2]) == ['int', 'float']

def test_eval_shape_list2():
    assert shape([[1, 2, 2, 2], [1, 2, 2, 2]]) == [['int']]

def test_eval_shape_list3():
    assert shape([[1, 2, 2.0, 2], [1, 2, 2.0, 2]]) == [['int', 'float']]

def test_eval_shape_list4():
    assert shape([ 1, [1, 2, 2.0, 2], [1, 2, 2.0, 2]]) == ['int', ['int', 'float']]

def test_eval_shape_dict_empty():
    assert shape({}) == {}

def test_eval_shape_dict1():
    assert shape({"val": 1}) == {"val": "int"}

def test_eval_shape_dict2():
    assert shape({"val": 1, "nested": {"n1": 2}}) == {"val": "int", "nested": {"n1": "int"}}

def test_eval_shape_dict2():
    d = [
        {"val": 1, "nested": {"n1": 2}},
        {"val": 1, "nested": {"n1": 2, "extra": "hello"}}
    ]

    assert shape(d) == [{"val": "int", "nested": {"n1": "int", "extra?": "str"}}]

def test_eval_shape_dict3():
    json_str = """
    {
        "l1": {
            "l2p1": [1],
            "l2p2": ["x"]
        }
    }
    """

    json_obj = json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))

    assert shape(json_obj) == {"l1": {"l2p1": ['int'], "l2p2": ["str"]}}

def test_eval_shape_dict4():
    obj = {
            "l2p1": [("foo", (1,))],
            "l2p2": ("x", 123)
        }

    assert shape(obj) == {"l2p1": [("str", ('int',))], "l2p2": ("str", 'int')}

def test_shape_eval_get_attr_returns_shape():
    obj = {
        "l2p1": [("foo", (1,))],
        "l2p2": ("x", 123)
    }

    s = shape(obj)
    assert isinstance(s, DictShape)
    assert isinstance(s.l2p1, ListShape)

    s1 = s.l2p1[0]
    assert isinstance(s1, TupleShape), f"the shape is {type(s1)}"

def test_tuple_with_list():
    assert shape((1, 2, [1])) == ('int', 'int', ['int'])

def test_tuple_with_dict():
    assert shape((1, 2, {"foo": 1})) == ('int', 'int', {"foo": 'int'})

def test_tuple_with_dupes():
    assert shape((1, 2, 3)) == ('int', 'int', 'int')

def test_tuple_with_dupes_arr():
    assert shape([(1, 2, 3), (1, 2, 3)]) == [('int', 'int', 'int')]

def test_dict_sometimes_null():
    d1 = {"val": 1, "nested": {"n1": 2}}
    d2 = {"val": 1, "nested": None}
    s = shape([d1, d2])
    assert s == [{"val": "int", "nested?": {"n1": "int"}}]

def test_dict_only_null_props():
    d1 = {"val": 1, "nested": None}
    d2 = {"val": 1, "nested": None}
    s = shape([d1, d2])
    assert s == [{"val": "int", "nested?": "None"}]

def test_complex_obj_civitai():
    obj = get_civitai_sample()
    shape(obj.result.data.json.collection)
    #does not throw

def test_anon1():

    anon_model = [
        {'id': 1, 'data': {'detail': "some string"} },
        {'id': 2, 'data': {'detail': 123} },
        {'id': 3}
    ]

    result = shape(anon_model)

    assert result == [{'data?': {'detail': 'str|int'}, 'id': 'int'}]
    
def test_tuple_prim_none_combination():

    data = [
        ("x", 1, "y"),
        ("x", 1, "y"),
        ("x", None, "y"),
        ]
    
    actual = shape(data)

    assert actual == [("str", "int|None", "str")]

def test_tuple_obj_none_combination():

    data = [
        ("x", [1, 2, 3], "y"),
        ("x", {"foo": "bar"}, "y"),
        ("x", {"foo", "bar"}, "y"),
        ("x", (1, 2), "y"),
        ("x", None, "y"),
        ]
    
    actual = shape(data)

    assert actual == [("str", "list|dict|set|tuple|None", "str")]

def test_nonstandard_object_does_not_throw():
    doc = '''
    <body>
        <div>
            <h1>header</h1>
            <p>nothing</p>
        </div>
        <div style="position: absolute">
            <h2>header</h2>
            <p>nothing</p>
        </div>
        <p>foo</p>
    </body>
    '''
    soup = BeautifulSoup(doc, 'html.parser')
    expected = ['.NavigableString', '.Tag']
    actual = shape(list(soup.select_one('body div').children))
    assert actual == expected

    
def test_keyvaluepair():
    from typing import NamedTuple

    class KeyValuePair[K, V](NamedTuple):
        key:K
        value:V

    data = [
        KeyValuePair(key=1, value=['a', 'b']),
        KeyValuePair(key=2, value=['b', 'x'])
    ]

    expected = [KeyValuePair(key='int', value=['str'])]
    actual = shape(data)

    #must use str compare to ensure named tuples
    assert str(actual).strip() == str(expected).strip()
