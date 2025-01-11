TESTDIR         := "tests/"
PROJECTCACHE    := ".cache"
COV_HTML_DIR    := "{{PROJECTCACHE}}/coverage/coverage_html"
COVERAGE_ARGS   := "--testmon --testmon-noselect --cov=src --cov-config=pyproject.toml --cov-report=term:skip-covered --cov-fail-under=0 --cov-report=html:codeqa/coverage/html"
TESTMON_PREFIX  := 'TESTMON_DATAFILE=".cache/testmondata"'
PROFILING_ARGS  := ""
PROFILING_ARGS_ := "--profile --profile-svg --pstats-dir .cache/prof --element-number 0"
TEST_CFG_ARG    := "--config-file=pyproject.toml"
TESTMON_ARGS    := "--testmon --testmon-forceselect --no-cov"
STOP_FORWARDING := "python ./scripts/stop_port_forwarding.py"
TIMESTAMP       := 'date +"%Y-%m-%d %H:%M:%S.%3N"'
VIEWER          := "chromium"

alias mypy    := typecheck
alias l       := lint
alias d       := docs
alias ta      := test-all
alias t       := test
alias scalene := profile
alias cts     := check-test-structure

default:
    just --list

init:
    mkdir -p {{ PROJECTCACHE }}

typecheck path="$PWD":
    mypy --cache-dir .cache/mypy_cache {{ path }}
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_mypy

format:
    ruff format .

lint path="$PWD":
    mypy --cache-dir .cache/mypy_cache {{ path }}
    ruff check --fix {{ path }}
    ruff format {{ path }}

deal:
    python -m deal lint

pydeps-full:
    pydeps src/datethyme \
        --noshow \
        -T svg \
        --show-deps \
        -o codeqa/pydeps/datethyme-full.svg \
        --rmprefix datethyme. \
        > codeqa/pydeps/pydeps-full.json
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_pydeps_full

pydeps:
    pydeps src/datethyme \
        --noshow \
        -T svg \
        --show-deps \
        -o codeqa/dependencies/pydeps/datethyme.svg \
        --rmprefix datethyme \
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

snakefood:
    python -m snakefood3 src/ datethyme \
        --group codeqa/dependencies/snakefood/group.txt \
        > codeqa/dependencies/snakefood/datethyme.dot
    sed -i 's/dpi="150",/size="25,25!",\n            dpi="50",/' codeqa/dependencies/snakefood/datethyme.dot
    dot -T svg codeqa/dependencies/snakefood/datethyme.dot -o codeqa/dependencies/snakefood/datethyme.svg
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_snakefood

bandit:
    echo "not yet..."

pyflame:
    python -m pyflame -o codeqa/performance/pyflame/flamegraph.svg src/datethyme/__main__.py tree

perf:
    perf record -o codeqa/performance/perf/perf.data datethyme tree
    flamegraph -o codeqa/performance/flamegraph/flamegraph.svg --perfdata codeqa/performance/perf/perf.data

deply:
    deply analyze --config codeqa/dependencies/deply/deply.yaml --output codeqa/dependencies/deply/report.txt --report-format text
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_deply

check-test-structure:
    python scripts/check_test_structure.py
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_check_test_structure

check-imports:
    python scripts/check_imports.py
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_check_imports

smoke:
    pytest {{ TEST_CFG_ARG }} tests/smoke

test:
    {{ TESTMON_PREFIX }} pytest {{ TEST_CFG_ARG }} {{ TESTMON_ARGS }} {{ TESTDIR }} \
        || {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test_partial \
        && {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test

test-all:
    {{ TESTMON_PREFIX }} pytest {{ TEST_CFG_ARG }} {{ COVERAGE_ARGS }} {{ PROFILING_ARGS }} {{ TESTDIR }} \
        || {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test_all \
        && {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_test

docs:
    python scripts/mkdocs.py
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_docs

poetry:
    poetry lock
    poetry update
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_poetry

profile:
    python3 -m scalene.set_nvidia_gpu_modes
    # TODO

@view-cov:
    echo "Recency: `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_test`"
    {{ VIEWER }} `pwd`/codeqa/coverage/html/index.html &>/dev/null

@view-docs:
    echo "Recency: `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_docs`"
    {{ VIEWER }} `pwd`/docs/mkdocs/site/index.html &>/dev/null

@view-deps:
    echo "Recency:"
    echo "  `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_pydeps_full`"
    echo "  `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_pydeps`"
    echo "  `sed 's/.\{7\}$//' <<< cat {{ PROJECTCACHE }}/last_pydeps_simple`"
    {{ VIEWER }} `pwd`/codeqa/dependencies &>/dev/null

view-flamegraph:
    {{ VIEWER }} `pwd`/codeqa/performance &>/dev/null

sbom:
    python ./scripts/sbom.py
    {{ TIMESTAMP }} > {{ PROJECTCACHE }}/last_sbom

install-sops:
    ./scripts/installation/install_sops.sh
