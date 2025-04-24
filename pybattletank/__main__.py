import asyncio

from pybattletank.main import run, run_as_executable


def main() -> None:
    asyncio.run(run())


def executable() -> None:
    asyncio.run(run_as_executable())


if __name__ == "__main__":
    main()
