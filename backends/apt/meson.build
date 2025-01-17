add_languages('cpp')

cpp_compiler = meson.get_compiler('cpp')

gstreamer_dep = dependency('gstreamer-1.0')
gstreamer_base_dep = dependency('gstreamer-base-1.0')
gstreamer_plugins_base_dep = dependency('gstreamer-plugins-base-1.0')
appstream_dep = dependency('appstream', version: '>=0.12')
apt_pkg_dep = cpp_compiler.find_library('apt-pkg')

# Check whether apt supports ddtp
ddtp_flag = []
if cpp_compiler.compiles(
  '''
    #include <apt-pkg/pkgcache.h>
    int main () {
      pkgCache::DescIterator d;
      return 0;
    }
  ''',
  dependencies: [
    apt_pkg_dep
  ]
)
  ddtp_flag = ['-DHAVE_DDTP']
endif

shared_module(
  'pk_backend_apt',
  'pk-backend-apt.cpp',
  'acqpkitstatus.cpp',
  'acqpkitstatus.h',
  'apt-cache-file.cpp',
  'apt-cache-file.h',
  'apt-job.cpp',
  'apt-job.h',
  'apt-messages.cpp',
  'apt-messages.h',
  'apt-sourceslist.cpp',
  'apt-sourceslist.h',
  'apt-utils.cpp',
  'apt-utils.h',
  'gst-matcher.cpp',
  'gst-matcher.h',
  'pkg-list.cpp',
  'pkg-list.h',
  include_directories: packagekit_src_include,
  dependencies: [
    packagekit_glib2_dep,
    gmodule_dep,
    apt_pkg_dep,
    gstreamer_dep,
    gstreamer_base_dep,
    gstreamer_plugins_base_dep,
    appstream_dep,
  ],
  cpp_args: [
    '-DG_LOG_DOMAIN="PackageKit-APT"',
    '-DPK_COMPILATION=1',
    '-DDATADIR="@0@"'.format(join_paths(get_option('prefix'), get_option('datadir'))),
    ddtp_flag,
    # To avoid some errors on API change:
    '-Werror=overloaded-virtual',
    # style enforcement: always use the keyword, which helps to avoid API misuse
    '-Werror=suggest-override',
  ],
  link_args: [
    '-lutil',
  ],
  override_options: [
    'c_std=c11',
    'cpp_std=c++17'
  ],
  install: true,
  install_dir: pk_plugin_dir,
)

install_data(
  '20packagekit',
  install_dir: join_paths(get_option('sysconfdir'), 'apt', 'apt.conf.d'),
)

install_data(
  'pkconffile.nodiff',
  install_dir: join_paths(get_option('datadir'), 'PackageKit', 'helpers', 'apt'),
)
