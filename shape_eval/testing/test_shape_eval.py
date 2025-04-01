from collections import namedtuple
from ..shape_eval import eval_shape, ShapeNode, node_graph_to_obj, DictShape, ListShape, TupleShape
from types import SimpleNamespace
from .base_test import get_civitai_sample
import json

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
    d = 1
    s = eval_shape(d)
    assert s == 'int'

def test_eval_shape_list_empty():
    d = []
    s = eval_shape(d)
    assert s == []

def test_eval_shape_list():
    d = [1, 2, 2, 2]
    s = eval_shape(d)
    assert s == ['int']

def test_eval_shape_list1():
    d = [1, 2, 2.0, 2]
    s = eval_shape(d)
    assert s == ['int', 'float']

def test_eval_shape_list2():
    d = [[1, 2, 2, 2], [1, 2, 2, 2]]
    s = eval_shape(d)
    assert s == [['int']]

def test_eval_shape_list3():
    d = [[1, 2, 2.0, 2], [1, 2, 2.0, 2]]
    s = eval_shape(d)
    assert s == [['int', 'float']]

def test_eval_shape_list4():
    d = [ 1, [1, 2, 2.0, 2], [1, 2, 2.0, 2]]
    s = eval_shape(d)
    assert s == ['int', ['int', 'float']]

def test_eval_shape_dict_empty():
    d = {}
    s = eval_shape(d)
    assert s == {}

def test_eval_shape_dict1():
    d = {"val": 1}
    s = eval_shape(d)
    assert s == {"val": "int"}

def test_eval_shape_dict2():
    d = {"val": 1, "nested": {"n1": 2}}
    s = eval_shape(d)
    assert s == {"val": "int", "nested": {"n1": "int"}}

def test_eval_shape_dict2():
    d = [
        {"val": 1, "nested": {"n1": 2}},
        {"val": 1, "nested": {"n1": 2, "extra": "hello"}}
    ]

    s = eval_shape(d)
    assert s == [{"val": "int", "nested": {"n1": "int", "extra": "str"}}]

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
    s = eval_shape(json_obj)
    assert s == {"l1": {"l2p1": ['int'], "l2p2": ["str"]}}

def test_eval_shape_dict4():
    obj = {
            "l2p1": [("foo", (1,))],
            "l2p2": ("x", 123)
        }

    s = eval_shape(obj)
    assert s == {"l2p1": [("str", ('int',))], "l2p2": ("str", 'int')}

def test_shape_eval_get_attr_returns_shape():
    obj = {
        "l2p1": [("foo", (1,))],
        "l2p2": ("x", 123)
    }

    s = eval_shape(obj)
    assert isinstance(s, DictShape)
    assert isinstance(s.l2p1, ListShape)

    s1 = s.l2p1[0]
    assert isinstance(s1, TupleShape), f"the shape is {type(s1)}"

def test_tuple_with_list():
    tup = namedtuple("mytup", ["a", "b", "c"])
    t1 = tup(1, 2, [1])
    sh = eval_shape(t1)
    assert sh == ('int', 'int', ['int'])

def test_tuple_with_dict():
    tup = namedtuple("mytup", ["a", "b", "c"])
    t1 = tup(1, 2, {"foo": 1})
    sh = eval_shape(t1)
    assert sh == ('int', 'int', {"foo": 'int'})

def test_tuple_with_dupes():
    tup = namedtuple("mytup", ["a", "b", "c"])
    t1 = tup(1, 2, 3)
    sh = eval_shape(t1)
    assert sh == ('int', 'int', 'int')

def test_tuple_with_dupes_arr():
    tup = namedtuple("mytup", ["a", "b", "c"])
    t1 = [tup(1, 2, 3), tup(1, 2, 3)]
    sh = eval_shape(t1)
    assert sh == [('int', 'int', 'int')]

def test_dict_sometimes_null():
    d1 = {"val": 1, "nested": {"n1": 2}}
    d2 = {"val": 1, "nested": None}
    s = eval_shape([d1, d2])
    assert s == [{"val": "int", "nested?": {"n1": "int"}}]

def test_dict_only_null_props():
    d1 = {"val": 1, "nested": None}
    d2 = {"val": 1, "nested": None}
    s = eval_shape([d1, d2])
    assert s == [{"val": "int", "nested?": "None"}]

def test_complex_obj_civitai():
    obj = get_civitai_sample()
    eval_shape(obj.result.data.json.collection)
    #does not throw
