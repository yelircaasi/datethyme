# datethyme

A savory approach to date and time, built on Pydantic and datetime, with an emphasis on input validation and date/time arithmetic.

## Roadmap

- [ ] localization: add DateStrings class with defaults for popular languages and possibility to pass custom strings -> DateStrings.lookup("mon", 4), DateStrings.get_with_fallback(), DateStrings.format(date: Date)
- [ ] add `stdlib` and `tuple` and `namedtuple` and `dict` properties?
- [ ] add __iter__()  and items()?
- [ ] add add_hours, add_minutes, add_seconds to Time
- [ ] add TimeDelta object?
- [ ] rename span to interval
- [ ] remove DateRange in favor of DateRange: 'range' for discrete sequences, 'span' (or 'interval'?) for uncountable intervals
- [ ] rewrite using class Time(_Time), etc. to avoid mypy 'method-assign' error -> get rid of _interactions.py
      (use inheritance instead of monkey-patching; measure performance)
- [ ] 


## Type Interactions

### **

```
---------------------------------------------------------
|          |    Date      |     Time     |   DateTime   |
|----------|--------------|--------------|--------------|
| Date     | DateRange    |      ND      | DateTimeSpan |
| Time     |     ND       |   TimeSpan   |      ND      |
| DateTime | DateTimeSpan | DateTimeSpan | DateTimeSpan |
---------------------------------------------------------
```

### \&

```
---------------------------------------------------------
|          |    Date      |     Time     |   DateTime   |
|----------|--------------|--------------|--------------|
| Date     |      ND      |   DateTime   |      ND      |
| Time     |   DateTime   |      ND      |      ND      |
| DateTime |      ND      |      ND      |      ND      |
---------------------------------------------------------
```

```
--------------------------------------------------------------
|               |   DateRange  |    TimeSpan  | DateTimeSpan |
|---------------|--------------|--------------|--------------|
| DateRange     |   DateRange  |      ND      |      ND      |
| TimeSpan      |      ND      |    TimeSpan  |      ND      |
| DateTimeSpan  |      ND      |      ND      | DateTimeSpan |
--------------------------------------------------------------
```

Date ** Date -> DateRange
Time ** Time -> TimeSpan
DateTime ** DateTime -> DateTimeSpan

Date ** Time -> ND