{
    pkgs,
    pyproject-nix,
    uv2nix,
    pyproject-build-systems,
}: let
    # COMMON ====================================================================
    inherit
        (import ./variables-and-helpers.nix {inherit pkgs;})
        cliViaNix
        commonEnv
        commonVars
        dependencies
        dependencyGroups
        envName
        fhsSetupPoetry
        fhsSetupUv
        fhsShellHook
        fhsSystemPackages
        fhsVars
        getPythonExecutable
        packageExecutableName
        packageNameNix
        packageNamePython
        pkgEnvName
        pureShellHook
        pureVars
        python
        pythonPackages
        sourcePreference
        universalHook
        writeVars
        ;

    inherit (pkgs) lib;

    fhsDependencies =
        (
            if cliViaNix
            then dependencies.flex
            else []
        )
        ++ dependencies.nonPython
        ++ fhsSystemPackages;

    # UV2NIX ====================================================================
    workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ../.;};

    pyprojectOverlay = workspace.mkPyprojectOverlay {sourcePreference = "wheel";};

    pyprojectOverrides = _final: _prev: {};

    pythonSet = (
        pkgs.callPackage pyproject-nix.build.packages {inherit python;}
    ).overrideScope (
        lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            pyprojectOverlay
            pyprojectOverrides
        ]
    );

    editablePythonSet = pythonSet.overrideScope (
        workspace.mkEditablePyprojectOverlay {root = "$REPO_ROOT";}
    );

    virtualenvForDev = editablePythonSet.mkVirtualEnv
    envName
    {${packageNameNix} = dependencyGroups;};

    virtualenvForPackage = pythonSet.mkVirtualEnv
    pkgEnvName
    workspace.deps.default;

    pythonExecutableForDev = getPythonExecutable virtualenvForDev;
in {
    inherit packageNameNix;

    package = virtualenvForPackage;

    app = {
        type = "app";
        program = "${virtualenvForPackage}/bin/${packageExecutableName}";
    };

    uvPure = pkgs.mkShell {
        packages =
            [virtualenvForDev]
            ++ dependencies.nonPython
            ++ dependencies.flex;

        env =
            commonVars
            // {
                UV_NO_SYNC = "1";
                UV_PYTHON = pythonExecutableForDev;
                UV_PYTHON_DOWNLOADS = "never";
                NIX_PYTHON = pythonExecutableForDev;
                VIRTUAL_ENV = "${virtualenvForDev}";
            };

        shellHook = universalHook;
    };

    uvFHS =
        (pkgs.buildFHSUserEnv rec {
            name = "${envName}-fhs-uv";
            targetPkgs = [python pkgs.uv] ++ fhsDependencies;
            profile = ''
                ${universalHook}

                ${writeVars (commonVars // fhsVars)}

                ${fhsSetupUv}

                ${fhsShellHook}
            '';
        }).env;

    # poetryPure = pkgs.mkShell {
    #   shellHook = universalHook;
    #   env = commonVars;
    #   buildInputs =
    #     [python poetryEnvPure]
    #     ++ dependencies.nonPython
    #     ++ dependencies.flex;
    # };

    poetryFHS =
        (pkgs.buildFHSUserEnv rec {
            name = "${envName}-fhs-poetry";
            targetPkgs = [python pkgs.poetry] ++ fhsDependencies;
            profile = ''
                ${universalHook}

                ${writeVars (commonVars // fhsVars)}

                ${fhsSetupPoetry}

                ${fhsShellHook}
            '';
        }).env;
}
