# datethyme

## Roadmap

Note to self: Have a lot of low-hanging fruit in `./sketch/schedule.py`:

- [ ] fills in the gaps in datamodels
- [ ] refine type hierarchy and ensure protocol conformity
- [ ] get script running end-to-end with a sufficiently-complex MVP

- [x] 50 `TODO`s
- [ ] 2 ignore comments
- [x] 8 `noqa` comments (not necessary to remove all; just review carefully)
- [ ] 94 `NotImplementedError`s
- [x] go through and fix all `__getitem__` methods in one fell swoop
- [x] 10 `cast`s (review whether necessary)
- [ ] clean up type hierarchy/ontology -> what is needed where? -> esp. wrt_superunit ScheduledEntry, scheduling
- [ ] implement jscalendar package in repo jscalendar-py
- [ ] add nesting_mode to determine how nested time partitions are resized under different operations
- [ ] support time zone info (at least enough for conversion back to zoned stdlib types)
- [ ] make optimal use of `deal` (-> figure out what that will be)
- [ ] make optimal use of `hypothesis` (-> figure out what that will be)
- [ ] move all valuable code out of` _ranges_old.py` into newer type-parametrized classes
- [ ] immediate: clean up to remove all 'type: ignore' amd 'pyright: ignore' comments
- [ ] next step: clean up the types, map how everything fits together
- [ ] add `add_hours_strict` (fail if wrap) and `add_hours_maybe` (return None if wrap)
- [ ] add `minutes|seconds_elapsed` and `minutes|seconds_remaining` properties?
- [ ] Create sister package thymeline?
- [ ] add pydantic model for jscalendar -> see [icalendar](https://github.com/collective/icalendar)
      and the related projects listed
- [ ] add x_to_next and x_from_last methods for all time-related objects
- [ ] Next step: go from AbstractRange[T] to BaseRange[T] and implement everything common
    that can be implemented in a generic manner; leave the rest to the respective subclasses.
- [ ] Do the same for AbstractSpan[T] -> BaseSpan[T] and AbstractPartition[T] -> BasePartition[T]
- [ ] add add_x and maybe also subtract_x for time increments
- [ ] make Date.start -> DateTime [00:00] and Date.end -> DateTime [24:00]
- [ ] add next_second, last_second, next_minute, ... to time classes
- [ ] add representation as 12-hour time and .format(...) for DateTime and Time analogous to Date.format()]

## Type Ontology

- elementary types:
  - Date
  - Time
  - DateTime
- discrete range types

- span types

- task-like types (i.e. calendar entry-like types)
