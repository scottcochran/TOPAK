<!-- Layer: runtime · API specification · TOPAK source: trace replay (Mechanism.tla over recorded traces) -->

An API spec has no runtime layer of its own, but the OpenAPI ecosystem has two things that stand
where trace replay stands: **validation of live traffic against the spec**, and **generative
testing from the spec**. Both check the interface, never the state machine behind it.

**Live traffic checked against the contract** (request/response validation middleware):

```python
# openapi-core as ASGI middleware on the operator HTTP shim: every real request and response is
# validated against 03-record/api/lease.openapi.yaml; a violation is logged with the operation id.
from openapi_core import OpenAPI
from openapi_core.contrib.starlette.middlewares import StarletteOpenAPIMiddleware
app.add_middleware(StarletteOpenAPIMiddleware, openapi=OpenAPI.from_file_path("lease.openapi.yaml"))
```

**Generative conformance from the spec** (Schemathesis): the spec is the oracle, inputs are drawn
from its schemas, and every response must conform; stateful mode chains operations through `links`.

```bash
schemathesis run ../../03-record/api/lease.openapi.yaml --url http://localhost:18080 \
  --checks all --phases=examples,fuzzing,stateful --max-examples 500
```

What it reaches: a 201 whose body is not a twelve-field lease, a 409 with an unlisted reason, a
renewal that returns 201 for a request the schema says is invalid. What it cannot reach: a 201 for
a *valid-looking* widening, because "widening" is a relation between two leases and OpenAPI states
properties of one message. That is the gap between the interface layer and the model.
