<!-- Usage guide for syncing runtime orchestration utilities -->

# Runtime Orchestration

The `labtools runtime sync` command imports signal-handling and checkpoint orchestration primitives from the legacy `src/runtime` tree.

## Directory Layout

- `src/runtime/` (legacy project) — Source for job control utilities such as `jobs.py`.
- `src/labtools/runtime_modules/` — Destination package in labtools.

## Syncing Modules

```bash
labtools runtime sync \
  /Users/jpmcdonald/Code/tmp-wair-tools/wair-sparse/src/runtime \
  /Users/jpmcdonald/Code/labtools/src/labtools/runtime_modules \
  --module jobs.py
```

- Include additional modules (e.g., helpers) as needed.
- Overwrites existing files with the same names.

## Sanitisation Checklist

- Ensure signal choices (`SIGUSR1`, `SIGUSR2`, etc.) align with deployment environments (adjust if conflicts exist).
- Remove logging endpoints or telemetry IDs tied to client environments.
- Confirm default checkpoint/log directories are configurable.

## Integration Tips

- Wrap long-running workers with the imported `JobSession` to gain pause/resume and forced checkpoint support.
- Share the generated `RunContext` token/environment across parallel workers using environment variables.
- Coordinate with data environment managers so DuckDB connections and runtime limits use consistent configuration.

### Example

```python
from labtools.runtime_modules.jobs import JobSession
from labtools.core_modules.run_context import RunContext

ctx = RunContext(project="labtools-demo", env="lab")
session = JobSession(run_context=ctx, log_path="logs/loader.log")

while more_batches():
    session.wait_if_paused()
    batch = load_next()
    process(batch)
    session.heartbeat({"batch": batch.id})
    if session.should_checkpoint():
        checkpoint_state()
```



