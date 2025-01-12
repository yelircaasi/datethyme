{
  description = "An flake to use a Python poetry project in an FHS environment when poetry2nix is uncooperative";
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/f7542cb59c3215123304811023035d4470751b2f";
    };

    flake-utils = {
      url = "github:numtide/flake-utils/11707dc2f618dd54ca8739b309ec4fc024de578b";
    };

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix/64fedcac9fb75016f8f421a5a5587352d6482df6";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix/1daa3dd83abcfa95c08d6b3847e672bd90e0c9d8";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs/68b4c6dae0c47974bda803cf4e87921776f6081d";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

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
