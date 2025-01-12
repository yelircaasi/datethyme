{pkgs}: let
  buildPythonPackage = pkgs.python3Packages.buildPythonPackage;
in {
  datethyme = buildPythonPackage rec {
    pname = "datethyme";
    version = "0.2.0";
    format = "pyproject";

    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-oJTU6sEKNyYssuF0q7ySDyaNLQVNOdpN0BwZ8ZX9AmE=";
    };

    buildInputs = [pkgs.python3Packages.poetry-core];

    propagatedBuildInputs = with pkgs.python3Packages; [
      multipledispatch
      pydantic
      deal
    ];

    nativeCheckInputs = with pkgs.python3Packages; [
      pytest
    ];

    doCheck = false;

    meta = with pkgs.lib; {
      description = "Ergonomic date and time types built on Pydantic and datetime.";
      homepage = "https://yelircaasi.github.io/datethyme";
      license = licenses.gpl3;
    };
  };
}
