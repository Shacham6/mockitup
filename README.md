![Logo](imgs/logo.svg)

`mockitup` is a small package that provides a DSL for quickly configuring mock behaviors.

<!-- You can read more in our [documentation](https://shacham6.github.io/mockitup/) website. -->

## Installation

Simply run the commands:

``` shell
> pip install [--upgrade] mockitup
```

## The `mockitup` library

You can easily use the `mockitup` DSL to configure `unittest.mock` objects.

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

The library has two main concepts that it uses to configure the mock objects: `allowances`, and `expectations`.

### Allowances

***Allowances*** let us give the mock _permission_ to be invoked in a certain way, without **requiring** it actually being invoked.

``` python
from unittest.mock import Mock
from mockitup import allow

mock = Mock()

allow(mock).add_five(5).returns(10)
allow(mock).add_five(1).returns(6)

assert mock.add_five(5) == 10  # That's fine, since we've allowed that to happen.

mock.add_five(4) # Will raise an `UnregisteredCall` exception!
```

You'll notice that we didn't call `mock.add_five(1)` and that's fine.
This is because we used the allow function, which doesn't enforce calls to be made.

If we do want to ensure that certain calls are made we can use the `expection_suite`.

### Expectations

***Expectations*** allow us to ensure that a mock is used in a certain way, in terms of both parameters and order.

``` python
from unittest.mock import Mock

from mockitup import expectation_suite

mock = Mock()
with expectation_suite() as es:
    es.expect(mock).add_five(1).returns(6)
    es.expect(mock).add_five(2).returns(7)
```

In the example shown above we initialized an `expectation_suite` inside a `with` clause.
Not fulfilling those expectations before the end of the `with` clause will result in the exception `ExpectationNotFulfilled` being raised.

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

Here you'll probably notice that we don't enforce order by default.
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

Click the following headings for details:

<details>
<summary>Call raises an exception</summary>

In order to make a method raise an exception when called with some input, simply use the `.raises` directive:

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

In most cases you'll want a mock to return a concrete value, but sometimes you'll want to make a call `yield_from` something.

In those cases you can use the `yields_from` directive:

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

Say we want to test the following function:

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

Each argument provided to the `returns` directive will be returned in turn.
On the first invocation of `read_line` the first argument will be returned, then the second, and so on...
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

<details>
<summary>Wildcard matching</summary>

Up until now, all of the examples presented so far included a strict parametrization of each `expect`ation and `allow`ence.
But, in some cases, a softer, more dynamic approach is prefered. Luckily, `mockitup` has you covered, in *plenty* of ways:

1. Use `ANY_ARG` when you know that there's an argument, but don't care about it's value:
    ``` python
    from unittest.mock import MagicMock
    from mockitup import ANY_ARG, allow

    mock = MagicMock()
    allow(mock).call(ANY_ARG, 2).returns(3)

    assert mock.call(1, 2) == 3
    mock.call(2, 2) == 3
    ```

2. Use `ANY_ARGS` when you don't care about **any** of the arguments provided to the mock:
    ``` python
    from unittest.mock import MagicMock
    from mockitup import ANY_ARGS, allow

    mock = MagicMock()
    allow(mock).call(ANY_ARGS).returns(1)

    assert mock.call(1) == 1
    assert mock.call("lol", 123) == 1
    assert mock.call([1, 0.1], False, "You get the point") == 1


3. Use `PyHamcrest` matchers in order to define expected constraints over the arguments, without defining concrete values:

    ``` python
    from unittest.mock import Mock
    from mockitup import allow
    from hamcrest import any_of

    picky_eater = Mock()

    allow(picky_eater).eat(any_of("pizza", "hamburger")).returns("yum")
    allow(picky_eater).eat(ANY_ARGS).raises(ValueError())

    assert picky_eater.eat("pizza") == "yum"
    assert picky_eater.eat("hamburger") == "yum"

    picky_eater.eat("vegetables")  # Will raise a value error.
    ```

</details>
