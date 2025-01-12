{ pkgs, lib, config, inputs, ... }:

{

  name = "vibrant";

  # https://devenv.sh/languages/
  dotenv.enable = true;
  languages.python = {
    enable = true;
    uv.enable = true;
  };


  enterShell = ''
    git --version
  '';

}
