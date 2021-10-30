# Easier `unittest.mock` configuration for the masses

`mockitup` is a small package which provides a small DSL for quickly
configuring mock behaviors.

You read more at our [documentation](https://shacham6.github.io/mockitup/).

## Installation

Simple run the commands:

``` shell
> pip install [--upgrade] mockitup
```

Adding the `--upgrade` flag will result in an upgrade of the package,
if an older version of `mockitup` is already installed in your environment.

## The `mockitup` library

Using `mockitup` is simple. It offers a small DSL to configure `unittest.mock` objects, which is easy to learn.

``` python
from unittest.mock import Mock
from mockitup import allow

# Configure the mock
mock = Mock()
allow(mock).add_five(4).returns(9)
allow(mock).add_five(5).returns(10)

# And now to use the mock
assert mock.add_five(4) == 9  # SUCCESS
assert mock.add_five(5) == 10 # SUCCESS
assert mock.add_five(3) == 8  # FAILED. WE DIDN'T ALLOW THAT TO HAPPEN.
```

To be effective with the library, you'll only need to learn
the difference between `allowances`, and `expectations`.

### Allowances

***Allowance*** is giving the mock _permission_ to being invoked in a certain way, but without any requirement of it actually being invoked.

``` python
from unittest.mock import Mock
from mockitup import allow

mock = Mock()

allow(mock).add_five(5).returns(10)
allow(mock).add_five(1).returns(6)

assert mock.add_five(5) == 10  # That's fine, since we've allowed that to happen.

# ...But calling the mock with an unregistered call will
# result in an exception called `mockitup.composer.UnregisteredCall`
# to be raised, since we didn't explicitly allow this call to be made!
mock.add_five(4)
```

You noticed how we didn't call `mock.add_five(1)`? Although we explicitly
allowed that to happen, we don't enforce them to be made.
But what if we DO want to enforce those calls to be made? Simple,
we use `expectation_suite`.

### Expectations

***Expectation*** is assuring that the mock is being used in a certain way, in terms of parameters and in order.

``` python
from unittest.mock import Mock

from mockitup import expectation_suite

mock = Mock()
with expectation_suite() as es:
    es.expect(mock).add_five(1).returns(6)
    es.expect(mock).add_five(2).returns(7)
```

Here we initialized an `expectation_suite`, inside a with caluse.
Inside the with clause, we defined our expectations:

1. We'll call `mock.add_five(1)` (which will return 6).
2. We'll call `mock.add_five(2)` (which will return 7).

Not fulfilling those expectations before the end of the `with` clause will result in an
exception called `ExpectationNotFulfilled` to be raised, which'll contain information
about the first unmet expectation. In our example:

``` text
mockitup.composer.ExpectationNotFulfilled: Expected mock `mock.add_five` to be called with (args: '(1,)', kwargs: '{}'), but wasn't
```

Invoking the mock as expected will result in the `with` clause passing silently, not
raising any errors:

``` python
from unittest.mock import Mock

from mockitup import expectation_suite

mock = Mock()
with expectation_suite() as es:
    es.expect(mock).add_five(1).returns(6)
    es.expect(mock).add_five(2).returns(7)

    assert mock.add_five(2) == 7
    assert mock.add_five(1) == 6

```

Here you'll probably notice a quirky detail: Yes, we're not enforcing the order by default.
In order to enforce the order, simply pass `ordered=True` to the `expectation_suite`:

``` python
from unittest.mock import Mock

from mockitup import expectation_suite

mock = Mock()
with expectation_suite(ordered=True) as es:
    es.expect(mock).add_five(1).returns(6)
    es.expect(mock).add_five(2).returns(7)

    assert mock.add_five(2) == 7
    assert mock.add_five(1) == 6

```

Running that code snippet will result in the exception `ExpectationNotMet` to be raised:

``` text
mockitup.composer.ExpectationNotMet: Expectations were fulfilled out of order
```

But if we were to run it in the configured order - everything would be fine:

``` python
from unittest.mock import Mock

from mockitup import expectation_suite

mock = Mock()
with expectation_suite(ordered=True) as es:
    es.expect(mock).add_five(1).returns(6)
    es.expect(mock).add_five(2).returns(7)

    assert mock.add_five(1) == 6
    assert mock.add_five(2) == 7

```

## Extra features

`mockitup` contains more features that allow you to test your code more
efficiently.

Click the following heading for details.

<details>
<summary>Call raises an exception</summary>
To make a method call raise an exception, simply use the `.raises` directive:

``` python
from unittest.mock import Mock

from mockitup import allow

mock = Mock()

allow(mock).divide(0).raises(ZeroDivisionError("You done goofed"))

mock.divide(0)  # ZeroDivisionError: You done goofed
```
</details>

<details>
<summary>Call yields from iterable</summary>
While most of the time you'll return concrete values, sometimes you'll want to make a
call yield from something.
For that, you can use the `yields_from` directive:

``` python
from typing import Iterator
from unittest.mock import Mock

from mockitup import allow

mock = Mock()

allow(mock).iter_numbers().yields_from([1, 2, 3, 4])

result = mock.iter_numbers()

assert isinstance(result, Iterator)
assert not isinstance(result, list)

for actual, expected in zip(result, [1, 2, 3, 4]):
    assert actual == expected
```

</details>

<details>
<summary>Multiple return values</summary>
When testing an impure function or method, sometimes it'll be tough to test using regular
`unittest.mock` objects.

Here's a function we want to test, for example:

``` python
def count_comments_in_line_reader(line_reader):
    commented_out_lines = 0
    while (line := line_reader.read_line()):
        if line.startswith("#"):
            commented_out_lines += 1
    return commented_out_lines
```

Here we see that the function calls the method called `read_line` possible multiple times,
each time possibly resulting in a different value.

Let's test that function:

``` python
from unittest.mock import Mock

from mockitup import allow

mock = Mock()
allow(mock).read_line().returns(
    "First line",
    "# Comment",
    "Second line",
    "# Comment",
    "# Comment",
    "Last line",
    None,
)

assert count_comments_in_line_reader(mock) == 3
```

Each argument provided to the `returns` directive will be returned in it's turn.
First will be returned the first argument, and on second invocation will be returned the second argument, and so on.

When all return values are exhausted, the last return value will be repeatedly returned on each future invocation:

``` python
from unittest.mock import Mock

from mockitup import allow

mock = Mock()
allow(mock).pop_number().returns(1, 2, 3)

assert mock.pop_number() == 1
assert mock.pop_number() == 2
assert mock.pop_number() == 3
assert mock.pop_number() == 3
assert mock.pop_number() == 3
assert mock.pop_number() == 3
```

</details>
