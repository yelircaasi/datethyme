# datethyme

Ergonomic date and time types built on Pydantic and datetime.

## Roadmap

- [ ] localization: add DateStrings class with defaults for popular languages and possibility to pass custom strings -> DateStrings.lookup("mon", 4), DateStrings.get_with_fallback(), DateStrings.format(date: Date)
- [ ] add `tuple` and `namedtuple` and `dict` properties?
- [ ] add __iter__()  and items()?
