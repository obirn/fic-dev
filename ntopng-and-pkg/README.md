# Script Ntopng & PKG

## Ntopng

1. `command_compilation.sh` : Setup et compile les projets nécessaires pour ntopng (le plus important est le respect des commits).

## PKG

1. `setup_pkg.sh` : Crée l'arborescence du package non compressé. Doit être lancé au même niveau de ntopng et génèrera ntopng-build.
    * A lancer sur un freebsd de compilation.
2. `generate_metadata.sh` : Crée les fichiers **+MANIFEST** et **+COMPACT_MANIFEST**, prend en argument le dossier ntopng-build.
    * A lancer sur un freebsd de compilation.
3. `install_ntopng.sh` : Effectue l'installation du package **/tmp/ntopng-6.5.250611.pkg**.
    * A lancer sur le pfsense pour installation.