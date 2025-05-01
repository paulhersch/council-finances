{
  description = "Flake für Finanztools des FSR Mathe/Info";
  # nixpkgs unstable ist implizit definiert
  outputs =
    { self
    , nixpkgs
    , ...
    }@inputs:
    let
      systems = [
        "x86_64-linux"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            config = {
              allowUnfree = true;
            };
          };
        in
        f pkgs);

      # Sammle alle Requirements ein und Mappe auf Pypkgs (also pkgs.python3Packages)
      required_python = (pypkgs:
        builtins.map (p: builtins.getAttr p pypkgs) (
          builtins.filter (x: x != "") (
            nixpkgs.lib.strings.splitString "\n" (
              builtins.readFile (./requirements.txt)
            )
          )
        )
      );

      dev_python = (pypkgs: with pypkgs; [
        pytest
        setuptools-scm
      ] ++ required_python pypkgs);
    in
    {
      devShells = forAllSystems (pkgs:
        let
          pypkgs = pkgs.python3.withPackages (p: dev_python p);
        in
        {
          default = pkgs.mkShell {
            nativeBuildInputs = [
              pypkgs
              # convenience script
              (pkgs.writeShellScriptBin "dev-run" ''
                python -m finanztool $@
              '')
              (pkgs.writeShellScriptBin "dev-test" ''
                python -m pytest
              '')
            ];
            PYTHONPATH = "${pypkgs}/${pypkgs.sitePackages}";
            VIRTUAL_ENV="${pypkgs}";
          };
        });

      formatter = forAllSystems (pkgs: pkgs.nixpkgs-fmt);
      packages = forAllSystems (pkgs: {
        default = pkgs.python3Packages.buildPythonPackage rec {
          name = "fsr-finanztools";
          src = ./.;
          propagatedBuildInputs = required_python pkgs.python3Packages;
        };
      });
    };
}
