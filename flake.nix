{
    description = "Python development flake.";
    inputs = {
        nixpkgs = {
            url = "github:nixos/nixpkgs/c57a028c30068aa2a7e00fa87300804dab748ff5";  # updated 2026-10-27
        };

        flake-utils = {
            url = "github:numtide/flake-utils/b7a79d3fea1e214f6d668d521cecec0c01e26544";  # updated 2026-10-27
        };

        pyproject-nix = {
            url = "github:pyproject-nix/pyproject.nix/ddc400a6883b042646d0940e65971bb7f7e96107";  # updated 2026-10-27
            inputs.nixpkgs.follows = "nixpkgs";
        };

        uv2nix = {
            url = "github:pyproject-nix/uv2nix/0fdaa03ea3c3c16dbb1fe4d69108f07227a4b42d";  # updated 2026-10-27
            inputs.pyproject-nix.follows = "pyproject-nix";
            inputs.nixpkgs.follows = "nixpkgs";
        };

        pyproject-build-systems = {
            url = "github:pyproject-nix/build-system-pkgs/a17819c85163988e063806ffc4f6d2716bc8ead8";  # updated 2026-10-27
            inputs.pyproject-nix.follows = "pyproject-nix";
            inputs.uv2nix.follows = "uv2nix";
            inputs.nixpkgs.follows = "nixpkgs";
        };
    };
    outputs = {
        self,
        nixpkgs,
        flake-utils,
        pyproject-nix,
        uv2nix,
        pyproject-build-systems,
    }:
        flake-utils.lib.eachDefaultSystem (system: let
            pkgs = import nixpkgs {
                inherit system;
                config.permittedInsecurePackages = ["olm-3.2.16"];
            };

            envs = import ./nix/python-environments.nix {
                inherit
                    pkgs
                    pyproject-nix
                    uv2nix
                    pyproject-build-systems
                    ;
            };

            inherit (envs) packageNameNix;
        in {
            packages = {
                default = envs.package;
                ${packageNameNix} = envs.package;
            };

            apps = {
                default = envs.app;
                ${packageNameNix} = envs.app;
            };

            devShells = {
                default = envs.uvPure;
                uv = envs.uvPure;
                uvFHS = envs.uvFHS;
                poetryFHS = envs.poetryFHS;
            };

            legacyPackages = pkgs;
        });
}
