let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    (pkgs.python312Packages.python.withPackages (python-pkgs: with python-pkgs; [
      markdown
      setuptools
      requests
    ]))
  ];
}
