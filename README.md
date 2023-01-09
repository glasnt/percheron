# percheron

[![PyPI](https://img.shields.io/pypi/v/percheron.svg)](https://pypi.org/project/percheron/)
[![Changelog](https://img.shields.io/github/v/release/glasnt/percheron?include_prereleases&label=changelog)](https://github.com/glasnt/percheron/releases)
[![Tests](https://github.com/glasnt/percheron/workflows/Test/badge.svg)](https://github.com/glasnt/percheron/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/glasnt/percheron/blob/master/LICENSE)



## Installation

Install this tool using `pip`:

    pip install percheron

## Usage

For help, run:

    percheron --help

You can also use:

    python -m percheron --help

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd percheron
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
