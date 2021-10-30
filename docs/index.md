# Welcome to mockitup

`mockitup` is a small package which provides a small DSL for quickly
configuring mock behaviors.

## Installation

Simple run the commands:

``` shell
> pip install [--upgrade] mockitup
```

Adding the `--upgrade` flag will result in an upgrade of the package,
if an older version of `mockitup` is already installed in your environment.

## Differences between `mockitup` and vanilla `unittest.mock`

This point can't be stressed enough - `mockitup` **is not an independent mocking library**, but
rather a simple wrapper which provides an easier-to-use API for configuring `unittest.mock` objects.

Using `mockitup` is embracing `unittest.mock` - not abolishing it.
