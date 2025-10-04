pkgname=swiggets
pkgver=1759611345
pkgrel=1
pkgdesc="Widgets for swaybar i3bar"
arch=('any')
url="https://github.com/georgievgeorgi/swiggets"
depends=('python' 'python-pydantic' 'python-aiofiles' 'python-mpd2' 'python-psutil' 'python-pulsectl-asyncio' 'tk')

makedepends=('git' 'python-build' 'python-installer' 'python-setuptools' 'python-wheel')

optdepends=('noto-fonts-emoji: glyph support'
	    'ttf-font-awesome: glyph support'
	    'ttf-nerd-fonts-symbols: glyph support'
	    'xkb-switch: x11 keyboard layout support'
	    'mako: notification switch support for mako'
	    'dunst: notification switch support for dunst'
    )
license=('MIT')
provides=('swiggets')
conflicts=('swiggets')
source=("$pkgname::git+https://github.com/georgievgeorgi/swiggets")
md5sums=('SKIP')

pkgver() {
    cd "$srcdir/$pkgname"
    git show --no-patch --format='%ct'
}

build() {
    cd "$srcdir/$pkgname"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/$pkgname"
    python -m installer --destdir="$pkgdir" dist/*.whl
    install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
    install -Dm644 swiggets-sway.py "${pkgdir}/usr/share/${pkgname}/swiggets-sway-example.py"
    install -Dm644 swiggets-i3.py "${pkgdir}/usr/share/${pkgname}/swiggets-i3-example.py"
}
