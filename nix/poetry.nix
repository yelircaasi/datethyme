{
  pkgs,
  poetry2nix,
}: {
  pure = pkgs.mkShell {
    shellHook = ''
      export PYTHONPATH=$PWD/src:$PYTHONPATH
      export PYTHONWARNINGS="ignore"
      source .envrc
    '';
    buildInputs =
      [
        pkgs.python312
        (pkgs.poetry2nix.mkPoetryEnv {
          projectDir = ./.;
          pyproject = ./pyproject.toml;
          poetrylock = ./poetry.lock;
          editablePackageSources = {
            datethyme = ./src;
          };
          preferWheels = true;
          extras = [];
          groups = ["main" "dev" "docs" "test"];
        })
      ]
      ++ (with pkgs; [
        stdenv.cc.cc.lib
        zlib
        uv
        # poetry
        libuuid
        file
        libz
        gcc
        which
        olm
        openssh
        graphviz
        inferno # inferno-flamegraph
        flamegraph # flamegraph.pl
        cargo-flamegraph # flamegraph
        pre-commit
        python312Packages.ipython
        bandit
        black
        isort
        mypy
        pylint
        semver
        cyclonedx-python
        pydeps
        ruff
        just
        scalene
      ]);
  };

  fhs =
    (pkgs.buildFHSUserEnv rec {
      name = "datethyme";
      targetPkgs = pkgs: (with pkgs; [
        zlib
        poetry
        libuuid
        file
        libz
        gcc
        which
        # olm
        uv
      ]);
      profile = ''
        export LD_LIBRARY_PATH="/lib:$LD_LIBRARY_PATH:${pkgs.lib.makeLibraryPath [pkgs.libuuid]}"
        poetry install # add --no-root here if this is just a metapackage
        source "$(poetry env info --path)"/bin/activate
      '';
    })
    .env;
}
