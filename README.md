# shade-cli

> **Lector interactivo de manga estilo `ani-cli` para la terminal.**  
> Descarga y reproduce capítulos de manga directamente como PDF en tu visor favorito, sin anuncios, sin trackers y con navegación fluida entre capítulos. Compatible con **macOS** y **Arch Linux / Linux**.

```text
   _____ __               __        ________    ____
  / ___// /_  ____ _____/ /__     / ____/ /   /  _/
  \__ \/ __ \/ __ `/ __  / _ \   / /   / /    / /  
 ___/ / / / / /_/ / /_/ /  __/  / /___/ /____/ /   
/____/_/ /_/\__,_/\__,_/\___/   \____/_____/___/   
    Manga en terminal • Visor PDF nativo • Estilo ani-cli
```

---

## ✨ Características

- 🔍 **Búsqueda difusa interactiva**: Menú rápido con [`fzf`](https://github.com/junegunn/fzf) para encontrar series y capítulos.
- 🚫 **Cero anuncios**: Conecta directamente a la API REST y al CDN de imágenes WebP en alta resolución, esquivando scripts y popunders del navegador.
- ⚡ **Descarga en paralelo**: Carga todas las páginas de un capítulo simultáneamente en menos de 1 segundo.
- 📖 **Experiencia PDF nativa**: Compila las imágenes en un único archivo PDF optimizado y lo abre al instante en tu visor del sistema:
  - **macOS**: Abre en **Vista Previa** (con desplazamiento continuo y gestos trackpad).
  - **Arch Linux**: Compatible con `zathura`, `mupdf`, `evince`, `okular` o el predeterminado vía `xdg-open`.
- 🔁 **Flujo `ani-cli` continuo**: Al terminar un capítulo, presiona <kbd>Enter</kbd> en tu terminal para cargar y abrir automáticamente el siguiente.
- 💾 **Historial persistente (`-c`)**: Recuerda automáticamente el último manga y capítulo leído.
- 📦 **Modo descarga (`-d`)**: Empaqueta capítulos completos en archivos `.cbz` listos para coleccionar.

---

## 🚀 Instalación

### 🏔️ Arch Linux

#### 1. Instalar dependencias
```bash
sudo pacman -S python fzf graphicsmagick zathura zathura-pdf-mupdf xdg-utils
```
*(Nota: también es compatible con `imagemagick` en lugar de `graphicsmagick`).*

#### 2. Clonar e instalar
```bash
git clone https://github.com/TU_USUARIO/shade-cli.git
cd shade-cli

# Opción A: Con makepkg (PKGBUILD)
makepkg -si

# Opción B: Con Makefile tradicional
sudo make install
```

---

### 🍎 macOS

#### 1. Instalar dependencias (con Homebrew)
```bash
brew install fzf graphicsmagick
```

#### 2. Instalar el ejecutable
```bash
git clone https://github.com/TU_USUARIO/shade-cli.git
cd shade-cli
sudo make install
```
*(O simplemente añade `bin/shade-cli` a tu `$PATH`).*

---

## 🎮 Uso

### Búsqueda interactiva
```bash
shade-cli
```
Te pedirá el nombre del manga y desplegará `fzf` para seleccionar serie y capítulo.

También puedes pasar la búsqueda como argumento:
```bash
shade-cli "Chainsaw Man"
shade-cli "One Piece"
```

### Controles en la terminal (mientras lees)

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [Enter] Siguiente (Cap. 31)   [b] Anterior (Cap. 29)
 [r] Reabrir actual           [c] Cambiar capítulo     [q] Salir
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
shade-cli > 
```

- <kbd>Enter</kbd>: Descarga y abre el siguiente capítulo.
- <kbd>b</kbd>: Vuelve al capítulo anterior.
- <kbd>r</kbd>: Reabre el capítulo actual si cerraste el visor.
- <kbd>c</kbd>: Despliega de nuevo la lista de capítulos con `fzf`.
- <kbd>q</kbd>: Salir a la terminal.

---

### Opciones y banderas

```bash
# Continuar leyendo donde lo dejaste en tu última sesión:
shade-cli -c

# Modo descarga (guarda el capítulo en ./mangas/ como archivo .cbz):
shade-cli -d "Berserk"

# Ver versión:
shade-cli -v
```

---

## ⚙️ Configuración (Linux)

Por defecto en Linux, `shade-cli` intentará abrir el PDF con tu visor configurado en las siguientes variables de entorno:

```bash
# En tu ~/.bashrc o ~/.zshrc:
export MANGA_VIEWER="zathura"
# o
export PDFVIEWER="mupdf"
```

Si no se define ninguna, buscará en orden: `zathura` ➔ `mupdf` ➔ `xdg-open` ➔ `evince` ➔ `okular`.

---

## 📂 Estructura del Proyecto

```text
shade-cli/
├── bin/
│   └── shade-cli       # Ejecutable Python independiente
├── .gitignore          # Archivos ignorados por Git
├── LICENSE             # Licencia MIT
├── Makefile            # Instalador para sistemas Unix
├── PKGBUILD            # Especificación de paquete para Arch Linux / AUR
└── README.md           # Documentación
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.
