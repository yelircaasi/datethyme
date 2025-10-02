{
  description = "TODO: rewrite: A flake to use a Python poetry project in an FHS environment when poetry2nix is uncooperative";
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/a77b87719ff11d3d7ea2439c406361b6b0c4c56a"; # 2025-10-01
    };

    flake-utils = {
      url = "github:numtide/flake-utils/11707dc2f618dd54ca8739b309ec4fc024de578b"; # 2025-10-01
    };

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix/f6381d442f915899838a9d18a13a72fbe93c2ce9"; # 2025-10-01
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix/de6273a5d3189fcc4ec2ae7270d9ed922a155439"; # 2025-10-01
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs/dbfc0483b5952c6b86e36f8b3afeb9dde30ea4b5"; # 2025-10-01
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
