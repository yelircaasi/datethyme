{
  pkgs,
  pyproject-nix,
  uv2nix,
  pyproject-build-systems,
}: let
  inherit (pkgs) lib;

  workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ../.;};

  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  pyprojectOverrides = _final: _prev: {};

  python = pkgs.python312;

  pythonSet =
    (
      pkgs.callPackage pyproject-nix.build.packages {inherit python;}
    )
    .overrideScope
    (
      lib.composeManyExtensions [
        pyproject-build-systems.overlays.default
        overlay
        pyprojectOverrides
      ]
    );
in {
  pure = let
    editableOverlay = workspace.mkEditablePyprojectOverlay {
      root = "$REPO_ROOT";
      members = ["datethyme"];
    };

    editablePythonSet = pythonSet.overrideScope editableOverlay;

    virtualenv = editablePythonSet.mkVirtualEnv "datethyme-dev-env" workspace.deps.all;
  in
    pkgs.mkShell {
      packages =
        [
          virtualenv
        ]
        ++ (with pkgs; [
          uv
          ruff
          mypy
          python312Packages.ipython
        ]);

      env = {
        UV_NO_SYNC = "1";
        UV_PYTHON = "${virtualenv}/bin/python";
        UV_PYTHON_DOWNLOADS = "never";

        NIX_PYTHON = "${virtualenv}/bin/python";
      };

      shellHook = ''
        # Undo dependency propagation by nixpkgs.
        unset PYTHONPATH

        # Get repository root using git. This is expanded at runtime by the editable `.pth` machinery.
        export REPO_ROOT=$(git rev-parse --show-toplevel)

        source .envrc
      '';
    };

  fhs = pkgs.mkShell {
    packages = [
      python
      pkgs.uv
    ];
    env =
      {
        UV_PYTHON_DOWNLOADS = "never";
        UV_PYTHON = python.interpreter;
      }
      // lib.optionalAttrs pkgs.stdenv.isLinux {
        LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
      };
    shellHook = ''
      unset PYTHONPATH
    '';
  };
}
