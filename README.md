# pybattletank

[![Release](https://img.shields.io/github/v/release/linhns/pybattletank)](https://img.shields.io/github/v/release/linhns/pybattletank)
[![Build status](https://img.shields.io/github/actions/workflow/status/linhns/pybattletank/main.yml?branch=main)](https://github.com/linhns/pybattletank/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/linhns/pybattletank/branch/main/graph/badge.svg)](https://codecov.io/gh/linhns/pybattletank)
[![Commit activity](https://img.shields.io/github/commit-activity/m/linhns/pybattletank)](https://img.shields.io/github/commit-activity/m/linhns/pybattletank)
[![License](https://img.shields.io/github/license/linhns/pybattletank)](https://img.shields.io/github/license/linhns/pybattletank)

pybattletank is a simple tower defense game written using
[pygame](https://www.pygame.org/) to explore
game development and the Python packaging landscape.

The gameplay is based on Philipe-Henri Gosselin's well-written series [Discover
Python and Patterns](https://www.patternsgameprog.com/series/discover-python-and-patterns/).

![Demo](./docs/assets/images/pybattletank.gif)

Detailed documentation is available at <https://linhns.github.io/pybattletank/>.

## Installation

There are a number of ways to obtain the game:

- Install via [pip](https://github.com/pypa/pip):

  ```shell
  pip install pybattletank
  ```

  Then, run the game:

  ```shell
  pybattletank
  ```

  or:

  ```shell
  python -m pybattletank
  ```

- Run without installation using [uv](https://github.com/astral-sh/uv):

  ```shell
  uvx pybattletank
  ```

- Grab the binary for your operating system from the
[releases](https://github.com/linhns/pybattletank/releases) page.

## Usage

### Basic game controls

- `W`, `A`, `S`, `D` to move tank.
- **Left-click** to shoot.
- Arrow keys/`Enter` to select menu items.

### Adding levels

Beside the packaged levels, users can create custom ones. Read this [guide](https://linhns.github.io/pybattletank/creating_levels).

## Acknowledgements

- Philippe-Henri Gosselin (@philippehenri-gosselin) for the wonderful series
  Discover Python and Patterns. <https://www.patternsgameprog.com/series/discover-python-and-patterns/>
- Florian Mass (@fpgmass) for creating [cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
