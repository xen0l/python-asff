# Testing

## Local testing

When adding new or changing existing functionality, it is important to ensure that no regressions were introduced.
python-asff comes with a test suite that checks functionality.

Just run this from the root of the repository:

```bash
./tests/run.py
```

These tests will be run automatically during the Github Actions build. 
However, if you want to see if it will pass the tests, you can just run that quick command on your machine.
