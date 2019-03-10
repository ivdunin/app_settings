from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='app_settings',
    version='1.1',
    description='YAML for application configuration, lite version (inspired by Ruby gem "config")',
    url='https://github.com/ivdunin/app_settings',
    author='Ilya Dunin',
    author_email='ilya.mirea@gmail.com',
    license='MIT',
    packages=['app_settings'],
    long_description=long_description,
    install_requires=[
        'PyYAML>=3.13',
    ],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
