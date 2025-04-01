```
pip install shape_eval
```

## Guide

### Schema Evaluation - shape(...)

```
from shape_eval.service import shape

model = [
  {'id': 1, 'name': "a", 'data': {'detail': "some string"} },
  {'id': 2, 'name': "b", 'data': {'detail': 123} },
  {'id': 3, 'name': "c", 'data': None }
]

shape(model)
```

```
[{'data?': {'detail': 'str|int'}, 'id': 'int', 'name': 'str'}]
```
