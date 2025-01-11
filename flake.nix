{
  description = "An flake to use a Python poetry project in an FHS environment when poetry2nix is uncooperative";
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/f7542cb59c3215123304811023035d4470751b2f";
    };

    flake-utils.url = "github:numtide/flake-utils/11707dc2f618dd54ca8739b309ec4fc024de578b";

    poetry2nix = {
      url = "github:nix-community/poetry2nix/4af430dfed3cb579de2e6e304076647bbea60959";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
  };
  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      datethyme = pkgs.poetry2nix.mkPoetryApplication {
        projectDir = ./.;
        preferWheels = true;
        pyproject = ./pyproject.toml;
        poetrylock = ./poetry.lock;
      };
      pkgs = import nixpkgs {
        inherit system;
        overlays = [
          poetry2nix.overlays.default
          (final: _: {
          })
        ];
        config.permittedInsecurePackages = [
          "olm-3.2.16"
        ];
      };

      fhsEnv =
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
            olm
          ]);
          profile = ''
            export LD_LIBRARY_PATH="/lib:$LD_LIBRARY_PATH:${pkgs.lib.makeLibraryPath [pkgs.libuuid]}"
            poetry install # add --no-root here if this is just a metapackage
            source "$(poetry env info --path)"/bin/activate
          '';
        })
        .env;

      python = pkgs.python312.withPackages (py:
        with py; [
          (
            pkgs.poetry2nix.mkPoetryEditablePackage {
              python = pkgs.python312;
              projectDir = ./.;
              editablePackageSources = {
                datethyme = "${builtins.getEnv "PWD"}/src";
              };
            }
          )
        ]);

      liveEnv = pkgs.mkShell {
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
              groups = ["main" "dev" "mkdocs" "test"];
            })
          ]
          ++ (with pkgs; [
            stdenv.cc.cc.lib
            zlib
            poetry
            libuuid
            file
            libz
            gcc
            which
            olm
            openssh
            graphviz
            inferno  # inferno-flamegraph
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
      pwd = builtins.getEnv "PWD";
    in {
      packages.default = datethyme;
      devShells = {
        default = liveEnv;
        live = liveEnv;
        fhs = fhsEnv;
      };
      legacyPackages = pkgs;
    });
}
