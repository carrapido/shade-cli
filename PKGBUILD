# Maintainer: crpd
pkgname=shade-cli
pkgver=1.1.0
pkgrel=1
pkgdesc="Lector interactivo de manga estilo ani-cli para terminal con apertura automática en PDF"
arch=('any')
url="https://github.com/crpd/shade-cli"
license=('MIT')
depends=(
    'python'
    'fzf'
)
optdepends=(
    'graphicsmagick: Compilación ultra-rápida de PDFs de manga (recomendado)'
    'imagemagick: Alternativa para compilar páginas en PDF'
    'python-img2pdf: Alternativa en Python para compilar PDFs'
    'zathura: Visor minimalista de PDF enfocado en teclado (recomendado)'
    'zathura-pdf-mupdf: Motor PDF para zathura'
    'xdg-utils: Apertura del visor PDF predeterminado del sistema (xdg-open)'
)
source=()
md5sums=()

package() {
    cd "${srcdir}/.."
    install -Dm755 bin/shade-cli "${pkgdir}/usr/bin/shade-cli"
    install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
    install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"
}
