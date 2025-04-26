# CedarDB driver for Python.
![PyPI - License](https://img.shields.io/pypi/l/cedardb)
![PyPI - Version](https://img.shields.io/pypi/v/cedardb)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/:packageName)
[![📦🐍 Build and Release Python](https://github.com/surister/cedardb-python/actions/workflows/release.yml/badge.svg)](https://github.com/surister/cedardb-python/actions/workflows/release.yml)
[![🪛🐍 Run tests](https://github.com/surister/cedardb-python/actions/workflows/tests.yml/badge.svg)](https://github.com/surister/cedardb-python/actions/workflows/tests.yml)

A CedarDB driver for Python, based on psycopg3. It follows it's own Pythonic API design.

# Documentation

## Installation

uv
```shell
uv add cedardb
```
pipx
```shell
pipx install cedardb
```

## Sending a Query

```python
from cedardb import Client

client = Client(host='localhost', dbname='postgres', user='postgres', password='password')

result = client.query('CREATE TABLE metrics (ts TIMESTAMP, user_id INTEGER, message TEXT)')
print(result)
# QueryResponse(original_statement_type='CREATE',
#               columns=[],
#               row_count=-1,
#               duration=0,
#               exception=None,
#               error_message=None)

print(result.ok)
# True
```

## Selecting data
```python
from cedardb import Client

client = Client(...)
result = client.query("select * from metrics")

print(result)
# QueryResponse(original_statement_type='SELECT',
#               columns=['ts', 'user_id', 'message'],
#               row_count=3,
#               duration=0,
#               exception=None,
#               error_message=None)
for row in result:
    print(row)
# (datetime.datetime(2025, 4, 11, 16, 32, 30, 211770), 1, 'I want pizza!')
# (datetime.datetime(2025, 4, 11, 16, 32, 30, 216277), 2, 'What toppings?')
# (datetime.datetime(2025, 4, 11, 16, 32, 30, 218842), 1, 'Tunna and Onions')

print(row.as_table())
# +----------------------------+---------+------------------+
# | ts                         | user_id | message          |
# +----------------------------+---------+------------------+
# | 2025-04-11 16:32:30.211770 | 1       | I want pizza!    |
# | 2025-04-11 16:32:30.216277 | 2       | What toppings?   |
# | 2025-04-11 16:32:30.218842 | 1       | Tunna and Onions |
# +----------------------------+---------+------------------+
```
## Bulk insert using pipelining
````python
from cedardb import Client

client = Client(...)

# Create the table to insert the data to
result = client.query('CREATE TABLE if not exists metrics (ts TIMESTAMP, user_id INTEGER, message TEXT)')

# Generate some random rows
rows = [
    (datetime.datetime.now(), i, 'somemsg') for i in range(10)
]

# Bulk insert
r = client.insert_many('metrics', rows=rows)

# Check if the insert was successful and print the latest inserted values
if r.ok:
    print(
        client.query('select * from metrics order by ts desc').as_table()
    )
````


## Using a factory
```python
import dataclasses
import datetime

from cedardb import Client

client = Client(...)

@dataclasses.dataclass
class Message:
    ts: datetime
    user_id: int
    message: str


result = client.query("select * from metrics", factory=Message)

for row in result:
    print(row)
    
# Message(ts=datetime.datetime(2025, 4, 11, 16, 32, 30, 211770), user_id=1, message='I want pizza!')
# Message(ts=datetime.datetime(2025, 4, 11, 16, 32, 30, 216277), user_id=2, message='What toppings?')
# Message(ts=datetime.datetime(2025, 4, 11, 16, 32, 30, 218842), user_id=1, message='Tunna and Onions')
```

## Errors
On database errors you can tell `.query` to raise an exception or get the error 
on the `SQLResult` object (default).

### Default
```python
result = client.query('CREATE TABLE metrics (ts TIMESTAMP, user_id INTEGER, message TEXT)')

print(result)
# QueryResponse(original_statement_type='',
#               columns=[],
#               row_count=-1,
#               duration=0,
#               exception=DuplicateTable('relation "metrics" already exists'),
#               error_message='relation "metrics" already exists')
print(result.ok)
# False
```

You can now re-raise the exception if needed. Exceptions are `psycopg`'s.
```python
if result.exception:
    raise result.exception
#   File "/home/surister/PycharmProjects/cedardb-python/cedardb/client.py", line 39, in query
#     cur.execute(statement)
#     ~~~~~~~~~~~^^^^^^^^^^^
#   File "/home/surister/PycharmProjects/cedardb-python/.venv/lib/python3.13/site-packages/psycopg/cursor.py", line 97, in execute
#     raise ex.with_traceback(None)
# psycopg.errors.DuplicateTable: relation "metrics" already exists
```

### Raise exception on queries

```python
result = client.query(
    'CREATE TABLE metrics (ts TIMESTAMP, user_id INTEGER, message TEXT)',
    raise_exception=True
)
#   File "/home/surister/PycharmProjects/cedardb-python/cedardb/client.py", line 39, in query
#     cur.execute(statement)
#     ~~~~~~~~~~~^^^^^^^^^^^
#   File "/home/surister/PycharmProjects/cedardb-python/.venv/lib/python3.13/site-packages/psycopg/cursor.py", line 97, in execute
#     raise ex.with_traceback(None)
# psycopg.errors.DuplicateTable: relation "metrics" already exists
```

# License
This project is open-source under a MIT license.
