# shade-cli

Lee manga de [shademanga.com](https://shademanga.com) desde tu terminal. Buscas con `fzf`, eliges un capítulo y se abre como PDF en tu visor. Cuando lo cierras, un menú te deja pasar al siguiente, regresar, guardar el PDF o cambiar de capítulo.

```text
   _____ __               __        ________    ____
  / ___// /_  ____ _____/ /__     / ____/ /   /  _/
  \__ \/ __ \/ __ `/ __  / _ \   / /   / /    / /
 ___/ / / / / /_/ / /_/ /  __/  / /___/ /____/ /
/____/_/ /_/\__,_/\__,_/\___/   \____/_____/___/
    Manga desde tu terminal · v1.1.0
```

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Dónde quedan tus archivos](#dónde-quedan-tus-archivos)
- [Configuración](#configuración)
- [Solución de problemas](#solución-de-problemas)
- [Desarrollo](#desarrollo)

## Requisitos

| Qué | Para qué |
| --- | --- |
| Python 3.9 o superior | Correr shade-cli. Solo usa la biblioteca estándar. |
| [fzf](https://github.com/junegunn/fzf) | Las listas, la búsqueda y la tecla Esc para regresar. |
| GraphicsMagick, ImageMagick o img2pdf | Armar el PDF de cada capítulo. Basta con uno. En macOS también funciona `poppler`. |
| Un visor de PDF | macOS: Vista Previa (ya viene instalada). Linux: zathura, mupdf, evince, okular o el que abra `xdg-open`. |
| [timg](https://github.com/hzeller/timg) (opcional) | Leer dentro de la terminal con `-t`. |

## Instalación

### macOS

```bash
brew install fzf graphicsmagick
git clone https://github.com/carrapido/shade-cli.git
cd shade-cli
sudo make install
```

macOS trae `python3` con las Command Line Tools. Si prefieres otra versión: `brew install python`.

### Arch Linux

```bash
sudo pacman -S --needed python fzf graphicsmagick zathura zathura-pdf-mupdf
git clone https://github.com/carrapido/shade-cli.git
cd shade-cli
sudo make install
```

### Otras distribuciones de Linux

Instala con tu gestor de paquetes `python3`, `fzf`, `graphicsmagick` (o `imagemagick`) y un visor de PDF. Después sigue los mismos pasos de `git clone` y `sudo make install`.

### Sin sudo

```bash
make install PREFIX="$HOME/.local"
```

Revisa que `~/.local/bin` esté en tu `PATH`.

> Los paquetes para AUR y Homebrew están en preparación ([#1](https://github.com/carrapido/shade-cli/issues/1)).

### Actualizar y desinstalar

```bash
git pull && sudo make install   # actualizar
sudo make uninstall             # desinstalar (usa el mismo PREFIX con el que instalaste)
```

Desinstalar no borra tus PDF, descargas ni historial (ver [Dónde quedan tus archivos](#dónde-quedan-tus-archivos)).

## Uso

```bash
shade-cli               # te pregunta qué buscar
shade-cli berserk       # busca directo
shade-cli -c            # abre el último capítulo que leíste
shade-cli -d berserk    # descarga capítulos como .cbz
shade-cli -t berserk    # lee dentro de la terminal (requiere timg)
```

### Pantallas y teclas

shade-cli tiene cuatro pantallas. En todas puedes escribir para filtrar, **Enter** elige, **Esc** regresa a la pantalla anterior y **Ctrl-C** sale.

| Pantalla | Enter | Esc |
| --- | --- | --- |
| Buscar manga | Busca lo que escribiste. Si no hay coincidencia exacta, te muestra los títulos parecidos, así que aguanta typos como «naurto» o «berzerk» | Sale de shade-cli |
| Resultados | Abre la lista de capítulos | Regresa a *Buscar manga* |
| Capítulos | Abre el capítulo (con `-d`, lo descarga) | Regresa a *Resultados* |
| ¿Qué sigue? | Ejecuta la opción elegida | Regresa a *Capítulos* |

Los capítulos aparecen en orden de lectura (0.5, 1, 1.5, 2…).

**¿Qué sigue?** aparece después de abrir cada capítulo:

- **Siguiente**, **Reabrir** y **Anterior**: *Siguiente* y *Anterior* solo aparecen cuando ese capítulo existe.
- **Guardar PDF en carpeta…**: te pregunta la carpeta, ya prellenada con la de descargas. Puedes cambiarla; acepta `~`. Enter guarda e imprime la ruta completa; Esc cancela. En los dos casos regresas al menú.
- **Elegir otro capítulo**: regresa a la lista de capítulos.
- **Salir**.

### Opciones

| Opción | Qué hace |
| --- | --- |
| `-c`, `--continue` | Abre el último capítulo que leíste. Con Esc pasas a la lista de capítulos y después a *Buscar manga*. |
| `-d`, `--download` | En lugar de abrir capítulos, los descarga como `.cbz` en la carpeta de descargas y regresa a la lista para que bajes otro. |
| `-t`, `--terminal` | Muestra las páginas dentro de la terminal con `timg` en lugar del visor de PDF. |
| `-v`, `--version` | Muestra la versión. |
| `-h`, `--help` | Muestra la ayuda, las teclas y las rutas. |

## Dónde quedan tus archivos

| Qué | Dónde |
| --- | --- |
| PDF de cada capítulo que abres (caché) | `~/.cache/shade-cli/` |
| PDF que guardas desde el menú | La carpeta que elijas. Por defecto, `~/Downloads/shade-cli/<manga>/` |
| `.cbz` descargados con `-d` | `~/Downloads/shade-cli/<manga>/` |
| Historial para `-c` | `~/.config/shade-cli/history.json` |

Cada vez que abres un capítulo, shade-cli imprime la ruta de su PDF en caché. Un capítulo que ya está en caché se abre sin volver a descargarlo. La caché no se limpia sola; para liberar espacio:

```bash
rm -rf ~/.cache/shade-cli
```

## Configuración

Define estas variables en tu `~/.zshrc` o `~/.bashrc`:

| Variable | Efecto |
| --- | --- |
| `SHADE_DOWNLOAD_DIR` | Carpeta base de descargas en lugar de `~/Downloads/shade-cli`. Acepta `~`. Cada manga va en su propia subcarpeta. |
| `MANGA_VIEWER` o `PDFVIEWER` | **Solo Linux.** Visor de PDF que se usa. Si no defines ninguna, shade-cli prueba en orden `zathura`, `mupdf`, `xdg-open`, `evince` y `okular`. |

```bash
export SHADE_DOWNLOAD_DIR=~/Manga
export MANGA_VIEWER=zathura
```

En macOS, el PDF siempre se abre con tu visor predeterminado (normalmente Vista Previa).

## Solución de problemas

| Síntoma | Solución |
| --- | --- |
| `No se pudo compilar el PDF` | Instala `graphicsmagick`, `imagemagick` o `img2pdf`. |
| `No se detectó un visor PDF gráfico` (Linux) | Instala un visor (por ejemplo, `zathura zathura-pdf-mupdf`) o define `MANGA_VIEWER`. Mientras tanto, el mensaje muestra la ruta del PDF para que lo abras a mano. |
| Esc no hace nada y ves listas numeradas | No se encontró `fzf`. Instálalo. Sin fzf, Enter vacío o `q` regresan. |
| `-t` no muestra las páginas | Instala `timg`. |
| `El servidor no respondió a la búsqueda aproximada` | El sitio limita cuántas búsquedas acepta por minuto. Espera unos segundos y vuelve a buscar. |

## Desarrollo

```bash
make test   # corre las pruebas: python3 -m unittest discover -s tests
```

```text
bin/shade-cli   # el programa: un solo archivo de Python, sin dependencias externas
tests/          # pruebas con unittest
Makefile        # install, uninstall, test
PKGBUILD        # receta de paquete para Arch Linux
```

## Aviso

shade-cli no aloja contenido: consulta la API pública de shademanga.com y descarga las páginas que el sitio sirve. Los derechos de cada obra pertenecen a sus autores y editoriales.

## Licencia

[MIT](LICENSE)
