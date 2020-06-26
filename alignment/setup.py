from setuptools import setup, find_packages
import versioneer


setup(
    name='alignment',
    packages=find_packages(),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='alignment',
    author='Diljot Grewal',
    author_email='diljot.grewal@gmail.com',
    entry_points={'console_scripts': ['alignment = alignment.run:main']},
    package_data={'':['scripts/*.py', 'scripts/*.R', 'scripts/*.npz', 'scripts/*.pl', "config/*.yaml", "data/*"]}
)
