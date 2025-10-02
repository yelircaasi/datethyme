TESTDIR := "tests"
PROJECTCACHE := ".cache"
COV_HTML_DIR := "{{PROJECTCACHE}}/coverage/coverage_html"
COVERAGE_ARGS := "--cov --cov-config=pyproject.toml --cov-report=term:skip-covered --cov-report=html"
COVERAGE_ARGS_ := "--cov=datethyme --cov-config=pyproject.toml --cov-report=term:skip-covered --cov-fail-under=0 --cov-report=html:codeqa/coverage/html"
TESTMON_PREFIX := 'TESTMON_DATAFILE=".cache/testmondata"'
PROFILING_ARGS := ""
PROFILING_ARGS_ := "--profile --profile-svg --pstats-dir .cache/prof --element-number 0"
TEST_CFG_ARG := "--config-file=pyproject.toml"
TESTMON_ARGS := "--testmon --testmon-forceselect --no-cov"
STOP_FORWARDING := "python ./codeqa/scripts/stop_port_forwarding.py"
TIMESTAMP := 'date +"%Y-%m-%d %H:%M:%S.%3N"'
VIEWER := "$BROWSER"

alias mypy := typecheck
alias l := lint
alias d := docs
alias tc := test-cov
alias t := test
alias cs := check-structure
alias cmo := check-method-order
alias ci := check-imports
alias flame := flamegraph
alias perf := perf-flamegraph

default:
    just --list

commit:
    sh codeqa/scripts/format-staged.sh
    cz commit

format:
    treefmt

check:
    ruff check .

fix:
    ruff check --fix .

typecheck path="$PWD":
    mypy --cache-dir .cache/mypy_cache {{ path }}
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_mypy

ty path="$PWD":
    ty check 
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_ty

lint path="$PWD": format typecheck fix deal
    yamllint -c codeqa/configs/yamllint.yml codeqa/ mkdocs.yml lefthook.yml 

deal:
    python -m deal lint

@vulture:
    vulture

pydeps-full:
    pydeps src/datethyme \
        --noshow \
        -T svg \
        --show-deps \
        --pylib \
        -o codeqa/dependencies/pydeps/datethyme-full.svg \
        --rmprefix datethyme. \
        > codeqa/dependencies/pydeps/pydeps-full.json
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_pydeps_full

pydeps:
    pydeps src/datethyme \
        --noshow \
        -T svg \
        --show-deps \
        -o codeqa/dependencies/pydeps/datethyme.svg \
        --rmprefix datethyme. \
        --cluster \
        --max-module-depth 3 \
        > codeqa/dependencies/pydeps/pydeps.json
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_pydeps

pydeps-simple:
    pydeps src/datethyme \
        --noshow \
        -T svg \
        --show-deps \
        -o codeqa/dependencies/pydeps/datethyme-simple.svg \
        --cluster \
        --max-module-depth 2 \
        > codeqa/dependencies/pydeps/pydeps-simple.json
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_pydeps_simple

@view-deps:
    echo "Recency:"
    echo "  `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_pydeps_full`"
    echo "  `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_pydeps`"
    echo "  `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_pydeps_simple`"
    {{ VIEWER }} `pwd`/codeqa/dependencies &>/dev/null

snakefood:
    python -m snakefood3 src/ datethyme \
        --group codeqa/dependencies/snakefood/group.txt \
        > codeqa/dependencies/snakefood/datethyme.dot
    sed -i 's/dpi="150",/size="25,25!",\n            dpi="50",/' codeqa/dependencies/snakefood/datethyme.dot
    dot -T svg \
        codeqa/dependencies/snakefood/datethyme.dot \
        -o codeqa/dependencies/snakefood/datethyme.svg
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_snakefood

deply:
    deply analyze \
        --config codeqa/dependencies/deply/deply.yaml \
        --output codeqa/dependencies/deply/report.txt \
        --report-format text
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_deply

bandit:
    bandit -r src/datethyme/ --baseline codeqa/security/bandit/baselines/datethyme.json
    bandit -r codeqa/scripts/ --baseline codeqa/security/bandit/baselines/scripts.json

bandit-html:
    bandit -r src/datethyme/ --format html --output codeqa/security/bandit/datethyme.html --baseline codeqa/security/bandit/baselines/datethyme.json
    bandit -r codeqa/scripts/ --format html --output codeqa/security/bandit/scripts.html --baseline codeqa/security/bandit/baselines/scripts.json

view-bandit:
    {{ VIEWER }} codeqa/security/bandit

pyflame:
    python -m pyflame \
        --output-path codeqa/performance/pyflame/flamegraph.svg \
        codeqa/scripts/wrapper_pyflame.py

flamegraph:
    flamegraph -o codeqa/performance/flamegraph/flamegraph.svg -- datethyme

perf-flamegraph:
    sh codeqa/scripts/perf-flamegraph.sh

scalene:
    python3 -m scalene codeqa/scripts/wrapper_scalene.py --profile-all

view-flamegraphs:
    {{ VIEWER }} `pwd`/codeqa/performance &>/dev/null

smoke:
    pytest {{ TEST_CFG_ARG }} tests/smoke

test:
    {{ TESTMON_PREFIX }} pytest {{ TEST_CFG_ARG }} {{ TESTMON_ARGS }} {{ TESTDIR }} \
        || {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test_partial \
        && {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test

unit:
    {{ TESTMON_PREFIX }} pytest tests/unit {{ TEST_CFG_ARG }} {{ TESTMON_ARGS }} {{ TESTDIR }} \
        || {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test_partial \
        && {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test

test-cov:
    pytest {{ TEST_CFG_ARG }} {{ COVERAGE_ARGS }} {{ TESTDIR }}/ \
        || {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test_all \
        && {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test

@view-cov:
    echo "Recency: `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_test`"
    {{ VIEWER }} `pwd`/codeqa/coverage/html/index.html &>/dev/null

docs:
    mkdocs build

docs-lazy:
    python codeqa/scripts/lazy_mkdocs.py
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_docs

serve-docs:
    mkdocs serve

@view-docs:
    echo "Recency: `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_docs`"
    {{ VIEWER }} `pwd`/docs/site/index.html &>/dev/null

sbom:
    uv export --format requirements.txt > requirements.txt
    cyclonedx-py requirements > sbom.json
    python codeqa/scripts/jsonfmt.py 4 sbom.json
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_sbom

reqs:
    uv export --format requirements-txt > requirements.txt
