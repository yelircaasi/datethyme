{pkgs}: 
let
  custom = import ./custom-packages.nix {inherit pkgs;};
in rec {
  pythonMinorVersion = "13";

  packageNamePython = "datethyme";

  packageNameNix = "datethyme";

  packageExecutableName = "datethyme";

  dependencyGroups = ["dev" "docs" "test"] ++ (if cliViaNix then [] else "cli-utils");

  sourcePreference = "wheel";

  envName = "${packageNameNix}-dev-env";

  pkgEnvName = "${packageNameNix}-pkg-env";

  universalHook = ''
    # Undo dependency propagation by nixpkgs.
    unset PYTHONPATH
    export PYTHONPATH="$PWD/src:$PYTHONPATH"

    if [ -n NIX_PYTHON ];
      then export python=$NIX_PYTHON
    fi

    source .envrc

    # Get repository root using git. This is expanded at runtime by the editable `.pth` machinery.
    export REPO_ROOT=$(git rev-parse --show-toplevel)
  '';

  fhsShellHook = ''
    # Adjust library path for binaries that expect /lib etc.
    export LD_LIBRARY_PATH="/lib:$LD_LIBRARY_PATH:${pkgs.lib.makeLibraryPath [pkgs.libuuid]}"
  '';

  pureShellHook = ''

  '';

  python = pkgs."python3${pythonMinorVersion}";

  pythonPackages = pkgs."python3${pythonMinorVersion}Packages";

  cliViaNix = true;

  dependencies = {
    flex =
      (with custom; [
        mdformat-with-plugins
        mkdocs-with-plugins
      ])
      ++ (with pkgs; [
        uv
        just
        lefthook
        commitizen
        ruff
        toml-sort
        yamlfmt
        yamllint
        pythonPackages.vulture
        pythonPackages.radon
        pythonPackages.radon
        pydeps
        bandit
        cyclonedx-python
        mypy
        ty
      ]);
    nonPython =
      (with custom; [])
      ++ (with pkgs; [
        cargo-flamegraph
        flamegraph
        graphviz
        alejandra
        mdsf # alternative: markdown-code-runner
        treefmt
        shfmt
        jujutsu
        jjui
        graphviz
        perf-tools
        ripgrep
        fd
        bat
        sad
      ]);
  };

  fhsSystemPackages = pkgs: (with pkgs; [
    stdenv.cc.cc.lib
    zlib
    libuuid
    file
    libz
    gcc
    which
    openssh
  ]);

  commonVars = {};

  pureVars = {};

  fhsVars = pkgs.lib.optionalAttrs pkgs.stdenv.isLinux {
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
  };

  fhsSetupUv = ''
    # Tell uv to use the Nix-provided interpreter but allow downloads
    export UV_PYTHON_DOWNLOADS="1"
    export UV_PYTHON="${python.interpreter}"

    if [ -D .venv ]; then
      uv venv
      uv lock
    fi
    uv sync
  '';

  fhsSetupPoetry = ''
    # Tell uv to use the Nix-provided interpreter but allow downloads
    export POETRY_VIRTUALENVS_PATH=".venv"
    export POETRY_PYTHON="${python.interpreter}"

    if [ ! -d ".venv" ]; then
      poetry init
      poetry lock
    fi
    poetry install
  '';

  getPythonExecutable = pythonVirtualenv: "${pythonVirtualenv}/bin/python";

  getNixLicenseName = name:
    {
      "MIT" = "mit";
      "BSD-2-Clause" = "bsd2";
      "BSD-3-Clause" = "bsd3";
      "Apache-2.0" = "asl20";
      "GPL-2.0-only" = "gpl2Only";
      "GPL-2.0-or-later" = "gpl2Plus";
      "GPL-3.0-only" = "gpl3Only";
      "GPL-3.0-or-later" = "gpl3Plus";
      "LGPL-2.1-only" = "lgpl21Only";
      "LGPL-2.1-or-later" = "lgpl21Plus";
      "LGPL-3.0-only" = "lgpl3Only";
      "LGPL-3.0-or-later" = "lgpl3Plus";
      "MPL-2.0" = "mpl20";
      "AGPL-3.0-only" = "agpl3Only";
      "AGPL-3.0-or-later" = "agpl3Plus";
    }.${
      builtins.lower name
    };

  writeVars = varSet:
    pkgs.lib.concatStringsSep
    "\n"
    (
      pkgs.lib.attrsets.mapAttrsToList
      (k: v: ''export ${k}="${v}"'')
      varSet
    );
}
