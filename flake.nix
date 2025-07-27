{
  description = "Flake for webhookmaster project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        packages.default = pkgs.stdenv.mkDerivation {
          name = "webhookmaster";
          src = ./.;

          buildInputs = [
            pkgs.python3
            pkgs.nodejs
            pkgs.rustc
            pkgs.cargo
            pkgs.git
          ];

          # Uncomment and customize if you need build/install phases
          # buildPhase = ''
          #   echo "Building..."
          # '';

          # installPhase = ''
          #   mkdir -p $out
          #   cp -r * $out/
          # '';
        };

        devShell = pkgs.mkShell {
          buildInputs = [
            pkgs.python3
            pkgs.nodejs
            pkgs.rustc
            pkgs.cargo
            pkgs.git
          ];
        };
      }
    );
}
