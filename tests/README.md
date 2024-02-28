# Run unit tests

Unit tests must be run inside the semgr8s test docker image to ensure compatible file system.
The test image is build as target `tester`:

```bash
docker buildx build --target tester -t semgr8s:tester -f build/Dockerfile .
```

Run default unit tests:

```bash
docker run --rm -it -v ${PWD}/tests/:/app/tests/ semgr8s:tester
```

Or manually via:

```bash
docker run --rm -it -v ${PWD}/tests/:/app/tests/ semgr8s:tester pytest --cov=semgr8s tests/
```
