# datethyme

## Roadmap

- 81 `TODO`s
- 71 ignore comments
- 8 `noqa` comments (not necessary to remove all; just review carefully)
- 72 `NotImplementedError`s
- go through and fix all `__getitem__` methods in one fell swoop
- 8 `cast`s (review whether necessary)
- make optimal use of `deal` (-> figure out what that will be)
- make optimal use of `hypothesis` (-> figure out what that will be)
- move all valuable code out of` _ranges_old.py` into newer type-parametrized classes
- immediate: clean up to remove all 'type: ignore' amd 'pyright: ignore' comments
- next step: clean up the types, map how everything fits together
- add `add_hours_strict` (fail if wrap) and `add_hours_maybe` (return None if wrap)
- add `minutes|seconds_elapsed` and `minutes|seconds_remaining` properties?
- Create sister package thymeline?
- add pydantic model for jscalendar -> see [icalendar](https://github.com/collective/icalendar)
  and the related projects listed
- 

## Type Ontology

- elementary types:
  - Date
  - Time
  - DateTime
- discrete range types

- span types

- task-like types (i.e. calendar entry-like types)
