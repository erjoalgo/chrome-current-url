import os
import re
import json
import atexit
import distutils.spawn
from setuptools.command.install import install
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

VERSION = re.search("[0-9.]+", read("chromeurl/version.py")).group(0)

EXE = "chromeurl"
PACKAGE = "chromeurl"

def install_manifest(filename_sans_ext, manifest_dict, directory_candidates,
                     max_installations=float("inf")):
    installed_manifests = []
    for cand_maybe_tilde in directory_candidates:
        if len(installed_manifests) > max_installations:
            break
        cand = os.path.expanduser(cand_maybe_tilde)
        parent = os.path.dirname(cand)
        print("\tconsidering {}".format(cand))
        if not os.path.exists(cand) and os.path.exists(parent):
            # if parent exists, this could be the first native messaging host
            try:
                os.mkdir(cand)
            except Exception as ex:
                print("unable to mkdir {}: {}".format(cand, ex))

        if os.path.exists(cand):
            manifest_path = os.path.join(cand, "{}.json".format(filename_sans_ext))
            try:
                with open(manifest_path, "w") as fh:
                    json.dump(manifest_dict, fh, indent=4)
                    installed_manifests.append(manifest_path)
                    print("installed manifest at: {}".format(manifest_path))
            except Exception as ex:
                print("\tfailed to install manifest at {}:\n\t {}"
                             .format(manifest_path, ex))
    return installed_manifests


def install_native_host():
    """install chrome native host manifest file"""
    NATIVE_HOST_CANDIDATES = [
        # https://developer.chrome.com/extensions/nativeMessaging

        # OS X (system-wide)
        "/Library/Google/Chrome/NativeMessagingHosts/",
        "/Library/Application Support/Chromium/NativeMessagingHosts/",

        # OS X (user-specific, default path)
        "~/Library/Application Support/Google/Chrome/NativeMessagingHosts/",
        "~/Library/Application Support/Chromium/NativeMessagingHosts/",

        # Linux (system-wide)
        "/etc/opt/chrome/native-messaging-hosts/",
        "/etc/chromium/native-messaging-hosts/",

        # Linux (user-specific, default path)
        "~/.config/google-chrome/NativeMessagingHosts/",
        "~/.config/chromium/NativeMessagingHosts/"
    ]

    EXE_ABS = distutils.spawn.find_executable(EXE)

    host_name = "com.erjoalgo.chrome_current_url"
    extension_id = "eibefbdcoojolecpoehkpmgfaeapngjk"

    manifest = {
        "name": host_name,
        "description": "chrome current url native host component",
        "path": EXE_ABS,
        "type": "stdio",
        "allowed_origins": [
            "chrome-extension://{}/".format(extension_id)
        ]
    }
    installed_manifests = install_manifest(host_name, manifest, NATIVE_HOST_CANDIDATES)
    if not installed_manifests:
        print ("could not discover suitable installation directory")
        exit(1)

_post_install = install_native_host

class new_install(install, object):
    def __init__(self, *args, **kwargs):
        super(new_install, self).__init__(*args, **kwargs)
        atexit.register(_post_install)


setup(
    name="chromeurl",
    version=VERSION,
    author="Ernesto Alfonso",
    author_email="erjoalgo@gmail.com",
    description=("native messaging host component of chrome current url extension. "
                 "exposes the current chrome browser url via a REST endpoint"),
    license="GPLv3",
    keywords="chrome chromium url",
    url="https://github.com/erjoalgo/chrome-current-url",
    packages=[PACKAGE],
    # long_description=read('README'),
    install_requires=['flask'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
    ],
    entry_points={
        'console_scripts': [
            '{}={}.main:main'.format(EXE, PACKAGE),
        ]
    },
    cmdclass={
        'install': new_install,
    },
)


# Local Variables:
# compile-command: "python setup.py install --user"
# End:
