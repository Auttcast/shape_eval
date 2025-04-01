```
pip install shape_eval
```

## Guide

### Schema Evaluation - shape(...)

Working with an undocumented api? some complex web response model?

Here's a simple example, but also works great on complex models

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
