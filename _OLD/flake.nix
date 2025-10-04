{
    description = "An flake to use a Python poetry project in an FHS environment when poetry2nix is uncooperative";
    inputs = {
        nixpkgs = {
            url = "github:nixos/nixpkgs/908514a0885f889432825e9ac71842ca444e8bd5";
        };

        flake-utils = {
            url = "github:numtide/flake-utils/11707dc2f618dd54ca8739b309ec4fc024de578b";
        };

        pyproject-nix = {
            url = "github:pyproject-nix/pyproject.nix/e09c10c24ebb955125fda449939bfba664c467fd";
            inputs.nixpkgs.follows = "nixpkgs";
        };

        uv2nix = {
            url = "github:pyproject-nix/uv2nix/582024dc64663e9f88d467c2f7f7b20d278349de";
            inputs.pyproject-nix.follows = "pyproject-nix";
            inputs.nixpkgs.follows = "nixpkgs";
        };

        pyproject-build-systems = {
            url = "github:pyproject-nix/build-system-pkgs/7dba6dbc73120e15b558754c26024f6c93015dd7";
            inputs.pyproject-nix.follows = "pyproject-nix";
            inputs.uv2nix.follows = "uv2nix";
            inputs.nixpkgs.follows = "nixpkgs";
        };

        poetry2nix = {
            url = "github:nix-community/poetry2nix/ce2369db77f45688172384bbeb962bc6c2ea6f94";
            inputs.nixpkgs.follows = "nixpkgs";
            inputs.flake-utils.follows = "flake-utils";
        };
    };
    outputs = {
        self,
        nixpkgs,
        flake-utils,
        pyproject-nix,
        uv2nix,
        pyproject-build-systems,
        poetry2nix,
    }:
        flake-utils.lib.eachDefaultSystem (system: let
            pkgs = import nixpkgs {
                inherit system;
            };
            datethyme = (import ./nix/datethyme.nix {inherit pkgs;}).package;
            uvEnv = import ./nix/uv.nix {
                inherit
                    pkgs
                    pyproject-nix
                    uv2nix
                    pyproject-build-systems
                    ;
            };
            poetryEnv = import ./nix/poetry.nix {inherit pkgs poetry2nix;};
        in {
            packages = {
                inherit datethyme;
                default = datethyme;
            };
            devShells = {
                default = uvEnv.pure;
                uv = uvEnv.pure;
                fhsUv = uvEnv.fhs;
                poetry = poetryEnv.pure;
                fhsPoetry = poetryEnv.fhs;
            };
            legacyPackages = pkgs;
        });
}
