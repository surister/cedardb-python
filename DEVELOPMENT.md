## Clone the project

```shell
git clone https://github.com/surister/cedardb-python
```

The easiest way to work on the project is using `uv`

## Install dependencies
```shell
uv sync
```

## Run tests
Set `tests.settings.DATABASE` the correct CrateDB credentials.

```shell
uv run pytest
```

## Build

```shell
uv build
```

## Upload new version to pypi

Create a new release on github.com/surister/cedardb-python/releases and the workflow will
take care of it.