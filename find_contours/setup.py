from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['find_contours'],
    scripts=['node/find_contours_node'],
    package_dir={'': 'src'}
)

setup(**d)
