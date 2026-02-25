project(
  'leshade',
  version: '2.3',
  meson_version: '>=1.2.0',
  license: 'MIT',
  license_files: 'LICENSE',
)

app_dir = '/opt/leshade'

install_data('main.py', install_dir: app_dir, install_mode: 'rwxr-xr-x')

install_subdir('scripts_core', install_dir: app_dir)
install_subdir('utils', install_dir: app_dir)
install_subdir('widgets', install_dir: app_dir)
install_subdir('assets', install_dir: app_dir)

install_symlink('leshade',
  install_dir: get_option('bindir'),
  pointing_to: app_dir / 'main.py'
)

install_data('flatpak/io.github.ishidawg.LeShade.desktop',
  install_dir: get_option('datadir') / 'applications',
  rename: 'leshade.desktop'
)

install_data('assets/logo256.png',
  install_dir: get_option('datadir') / 'icons/hicolor/256x256/apps',
  rename: 'leshade.png'
)

install_data('LICENSE',
  install_dir: get_option('datadir') / 'licenses' / meson.project_name()
)
