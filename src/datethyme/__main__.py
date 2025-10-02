import deal
import loguru
import multipledispatch
import pydantic


def main() -> None:
    print("\n\n--- DEPENDENCIES INSTALLED ---")
    print(f"{pydantic.__name__} version: {pydantic.__version__}")
    print(f"{deal.__name__} version: {deal.__version__}")
    print(f"{multipledispatch.__name__} version: {multipledispatch.__version__}")
    print(f"{loguru.__name__} version: {loguru.__version__}")


if __name__ == "__main__":
    main()
