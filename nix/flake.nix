{
  description = "Chocofi";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    project-banner.url = "github:wallago/project-banner?dir=nix";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      project-banner,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells = {
          default = pkgs.mkShell {
            buildInputs = with pkgs; [
              python313Packages.west
              python313Packages.pyelftools
              python313Packages.setuptools
              python313Packages.protobuf
              cmake
              ninja
              protobuf
            ];
            shellHook = ''
              export ZEPHYR_BASE=$PWD/zephyr
              export CMAKE_PREFIX_PATH=$PWD/zephyr/share/zephyr-package/cmake
              export ZEPHYR_TOOLCHAIN_VARIANT=gnuarmemb
              export GNUARMEMB_TOOLCHAIN_PATH=${pkgs.gcc-arm-embedded}
              ${project-banner.packages.${system}.default}/bin/project-banner \
              --owner "wallago" \
              --logo " 󰖌 " \
              --product "keyboard" \
              --part "chocofi" \
              --code "WL25-KB-CHOCOFI" \
              --tips "For FreeCAD: f=\"$PWD/case/build.py\"; exec(open(f).read())" \
              --tips "west init -l config" \
              --tips "west update" \
              --tips "west build -d build/cl_studio -b nice_nano_v2 -s zmk/app -S studio-rpc-usb-uart -- -DSHIELD=chocofi_left -DCONFIG_ZMK_STUDIO=y -DBOARD_ROOT=$PWD" \
              --tips "west build -d build/cr -b nice_nano_v2 -s zmk/app -- -DSHIELD=chocofi_right -DBOARD_ROOT=$PWD"
            '';
          };
        };
      }
    );
}
