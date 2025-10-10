# datethyme

TODO:

- add `add_hours_strict` (fail if wrap) and `add_hours_maybe` (return None if wrap)
- add `minutes|seconds_elapsed` and `minutes|seconds_remaining` properties?

Running this project requires `copier`, `git`, `uv`, and `flake`. Install `nix` and
install the others by running `nix-shell -p uv python3 git`. You can now copy the project and run the toy CLI provided out-of-the-box:

```sh
copier copy --trust \
    /home/isaac/repos/dev-envs/python-uv-nix /tmp/hello-world \
    --data-file /home/isaac/repos/dev-envs/python-uv-nix/example-data-uv.yml

nix run /tmp/hello-world
```

You can also enter a development environment with all dependencies installed:

```sh
nix develop
```

Once in this dev shell, you have a number of development utils you can try out (via just):

```sh
✔just
✔just format
✔just check
✔just fix
✔just typecheck
✔just lint
✔just deal
✔just vulture
✔just pydeps-full
✔just pydeps
✔just pydeps-simple
✔just view-deps
✔just snakefood
✔just deply
✔just bandit
✔just bandit-html
✔just bandit-view
✔just pyflame
✔just flamegraph
✔just perf-flamegraph
✔just check-structure
✔just check-imports
✔just smoke
✔just unit
✔just test
✔just test-cov
☐ just docs
✔just scalene
✔just view-cov
☐ just view-docs
✔just view-flamegraphs
✔just sbom

lefthook validate
lefthook run all
```

## Roadmap

Add FilteredRange types (separate because they will behave differently)

Modify check_structure script to add inherited methods to subclasses (especially important for abstract classes)

[deal tests](https://deal.readthedocs.io/basic/tests.html)

[hypothesis tests](https://hypothesis.readthedocs.io/en/latest/)

0. ✔ Sync package lists in uv.nix.jinja and README.md

0. ✔ Parametrize each package for copier and update copier.yml

0. ✔ Clean up copier.yml and example-data.yml

0. ✔ Get impure environment working -> draw from buildFHSUserEnv approach in consilium and other projects

0. ✔ Write working version of scripts and test them on datethyme

0. ✔ create reference project (revised from datethyme)

0. ✔ use copier to re-create it (make a datethyme answers file)

0. ✔ find good CLI tools for diffing an entire folder

0. ✔ iteratively modify template until copier perfectly re-creates the reference project

0. ✔ package mdformat with mdformat-mkdocs (via nix)

0. ✔ remove super-linter, but look over it and steal any good ideas

0. ✔ add [commitizen](https://github.com/commitizen-tools/commitizen) and [commitmsgfmt](https://gitlab.com/mkjeldsen/commitmsgfmt) ✔

0. ✔ Modify nix to support any python version via [nixpkgs-python](https://github.com/cachix/nixpkgs-python) and [tox](https://tox.wiki/en/4.27.0/index.html)

0. ✔ Read through [jinja2-ansible-filters](https://gitlab.com/dreamer-labs/libraries/)

0. Go through https://www.youtube.com/results?search_query=nix+and+python and any relevant NixCon talks

0. ✔ restructure nix code

0. ✔ add poetry support (selectable via copier)

0. re-make datethyme package using template, iteratively polishing the template

0. add copier switch to include a CLI or not

### Later

Note: first get working the way it is for datathyme.

0. [conventional-changelog](https://github.com/conventional-changelog/conventional-changelog)

0. Package all docs packages via nix, since they run independently of the other Python packages.

0. Do the same for testing dependencies, if possible.

0. Add different types of git hooks

- Client-Side Hooks

    - **Pre-commit hooks** run before a commit is created and are ideal for code quality checks. They're perfect for running linters, formatters, static analysis tools, or tests to catch issues before they enter the repository. If the hook exits with a non-zero status, the commit is aborted

    - **Prepare-commit-msg hooks** execute after the default commit message is created but before the editor opens. These work well for automatically adding ticket numbers, branch names, or standardized formatting to commit messages based on branch patterns or other context

    - **Commit-msg hooks** run after you've written your commit message and are excellent for enforcing commit message conventions. They can validate that messages follow specific formats, contain required information like issue references, or meet length requirements

    - **Post-commit hooks** trigger after a commit completes successfully. Since they can't affect the commit outcome, they're useful for notifications, triggering builds, updating external systems, or logging commit information

    - **Pre-rebase hooks** run before rebasing and help prevent rebasing published commits or branches that shouldn't be rebased. They're particularly valuable for protecting main branches or enforcing workflow policies

    - **Post-checkout and post-merge hooks** execute after checking out branches or completing merges. These are ideal for environment setup tasks like updating dependencies, clearing caches, generating files, or syncing external resources that depend on the current branch state

- Server-Side Hooks

    - **Pre-receive hooks** run before any references are updated when receiving a push. They're powerful for enforcing repository-wide policies like preventing force pushes to protected branches, validating that all commits meet standards, or checking permissions before allowing updates

    - **Update hooks** execute once per branch being updated and are perfect for branch-specific policies. They can enforce different rules for different branches, validate individual commits, or check that updates follow branching strategies

    - **Post-receive hooks** run after all references are successfully updated and are ideal for deployment triggers, sending notifications, updating issue trackers, or kicking off CI/CD pipelines. Since they run after the push succeeds, they're commonly used for automation that depends on the repository being in its new state

## Dependency Classes

## Dependency Classes

TODO: look at jj-fzf, lazyjj, gg-jj look at luxuries

- dependency resolution (should already be installed)

    - [uv](https://github.com/astral-sh/uv) ✔

- miscellaneous (semver via Python)

    - [semver](https://github.com/python-semver/python-semver) ✔

- task running / hooks (installable via Python or Nix; Nix preferred)

    - [just](https://just.systems/man/en/) ✔
    - [lefthook](https://lefthook.dev/) ✔

- interactive programming (installable via Python or Nix; Nix preferred)

    - [ipython](https://ipython.org/) ✔

- static type checking (installable via Python or Nix; Nix preferred)

    - [mypy](https://mypy.readthedocs.io/en/stable/) ✔
    - [ty](https://github.com/astral-sh/ty) ✔

- source code visualization (graphviz and pydeps via Nix, the rest via Python)

    - [pydeps](https://github.com/thebjorn/pydeps) ✔
    - [graphviz](https://graphviz.org/) ✔
    - [deply](https://vashkatsi.github.io/deply/) ✔
    - [snakefood3](https://furius.ca/snakefood/) ✔
    - [grimp](https://grimp.readthedocs.io/en/stable/usage.html) ✔

- performance profiling (flamegraph and scalene via Nix, pyflame via Python)

    - [pyflame](https://pyflame.readthedocs.io/en/latest/) ✔
    - [scalene](https://github.com/plasma-umass/scalene) ✔
    - [flamegraph-rs](https://github.com/flamegraph-rs/flamegraph)
        (cargo-flamegraph in nix) ✔

- software supply chain, security (installable via Python, but Nix preferred)

    - [cyclonedx-python](https://github.com/CycloneDX/cyclonedx-python) ✔
    - [bandit](https://bandit.readthedocs.io/en/latest/) ✔

- testing (installed via Python for now)

    - [pytest](https://docs.pytest.org/en/stable/) ✔
    - pytest plugins: --> look at [these](https://github.com/man-group/pytest-plugins)
        - [mock](https://pytest-mock.readthedocs.io/en/latest/) ✔
        - [testmon](https://testmon.org/) ✔
        - [cov](https://pytest-cov.readthedocs.io/en/latest/) ✔
        - [loguru](https://github.com/mcarans/pytest-loguru) ✔
        - [profiling](https://github.com/man-group/pytest-plugins/tree/master/pytest-profiling) [video](https://www.youtube.com/watch?v=OexWnUTsQGU) ✔
    - [coverage](https://coverage.readthedocs.io/en/7.8.2/) ✔
    - [hypothesis](https://hypothesis.readthedocs.io/en/latest/) ✔
    - [tox](https://tox.wiki/en/4.26.0/) ✔

- docs (installed via Python for now)

    - [mkdocs](https://www.mkdocs.org/) ✔
    - [mkdocstrings](https://mkdocstrings.github.io/) ✔
    - [mkdocstrings-python](https://mkdocstrings.github.io/python/) ✔
    - [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) ✔
    - [pygments](https://pygments.org/) ✔

- formatters / linters

    - installable via Python or Nix:
        - [ruff](https://astral.sh/ruff) ✔
        - [mdformat](https://github.com/hukkin/mdformat) + [mdformat-mkdocs](https://github.com/KyleKing/mdformat-mkdocs) TODO
        - [yamlfmt](https://github.com/google/yamlfmt)
            OR [yamllint](https://github.com/adrienverge/yamllint) ✔
        - [pyprojectsort](https://github.com/kieran-ryan/pyprojectsort)
        - [toml-sort](https://github.com/pappasam/toml-sort) ✔
    - installable only via Nix or other package manager:
        - [treefmt](https://treefmt.com/latest/) + [treefmt-nix](https://github.com/numtide/treefmt-nix) ✔
        - [alejandra](https://github.com/kamadorueda/alejandra) ✔
        - [super-linter](https://github.com/super-linter/super-linter) TODO
        - [markdown-code-runner](https://github.com/drupol/markdown-code-runner)
            OR [mdsf](https://github.com/hougesen/mdsf) ✔
        - [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)
            OR [markdownlint-cli](https://github.com/DavidAnson/markdownlint-cli) TODO
        - [just-formatter](https://github.com/eli-yip/just-formatter) ✔

## To Look at for Later

- [pystackflame](https://pypi.org/project/pystackflame/)



# datethyme

A savory approach to date and time, built on Pydantic and datetime, with an emphasis on input validation and date/time arithmetic.

## Roadmap

- [ ] review which dunder methods to use for what
      - __init__
      - __repr__
      - __str__
      - __bool__
      - __eq__
      - __ne__
      - __hash__
      - __lt__
      - __gt__
      - __le__
      - __ge__
      - 
      - __int__
      - __float__
      - __bytes__
      - __complex__
      - __format__
      - __enter__
      - __exit__
      - 
      - __add__      +  : 
      - __sub__      -  :
      - __mul__      *  : 
      - __truediv__  /  : 
      - __mod__      %  : 
      - __floordiv__ // : 
      - __pow__:     ** : range creation
      - __matmul__    @ : 
      - 
      - __radd__
      - __rsub__
      - __rmul__
      - __rtruediv__
      - __rmod__
      - __rfloordiv__
      - __rpow__
      - __rmatmul__
      - 
      - __and__: composite from elementary
      - __or__        |  : composite span creation?
      - __xor__       ^  : inverse composite span (complement) creation?
      - __rshift__   >>  : span creation
      - __lshift__   <<  : reverse span creation?
      - __rand__      
      - __ror__
      - __rxor__
      - __rrshift__
      - __rlshift__
      - 
      - __neg__
      - __pos__
      - __invert__
      - 
      - __iadd__
      - __isub__
      - __imul__
      - __itruediv__     /=  : 
      - __imod__         %=  : 
      - __ifloordiv__   //=  : 
      - __ipow__        **=  : 
      - __imatmul__      @=  : 
      - __iand__         &=  : 
      - __ior__          |=  :
      - __ixor__         ^=  :
      - __irshift__     >>=  : 
      - __ilshift__     <<=  : 
      - 
      - __divmod__
      - __rdivmod__
      - __abs__
      - __index__
      - __round__
      - __trunc__
      - __floor__
      - __ceil__
      - 
      - __getattr__
      - __getattribute__
      - __setattr__
      - __delattr__
      - __dir__
      - 
      - __prepare__
      - __instancecheck__
      - __subclasscheck__
      - __init_subclass__
      - __subclasses__
      - __mro_entries__
      - __class_getitem__
      - 
      - __set_name__
      - __get__
      - __set__
      - __delete__
      - 
      - __buffer__
      - __release_buffer__
      - 
      - __new__
      - __del__
      - 
      - __aenter__
      - __aexit__
      - __aiter__
      - __anext__
      - __await__
      - 
      - 

- [ ] add round_hour(), round_minute(), etc.
- [ ] add support for conditional ranges (and maybe spans), for example
      DateRange(..., filter=lambda wd: wd < 6)
- [ ] add support for composite spans and ranges (union as opposed to hull)
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

---

Create sister package thymeline
