app\_settings module
====================

Simplify usage of YAML files for application configuration.

Inspired by Ruby Gem "config" https://github.com/railsconfig/config But
not all features implemented yet.

Usage example
-------------

Installation: ``pip install app_settings``

Create sample app with following structure:

.. code:: bash

    /my_app
      my_app.py
      /config
        settings.yml  # required file
        additional_settings.yml
        /settings
          production.yml
          stage.yml
          development.yml  # required file   

``AppSettings`` -- singleton, so it is not possible to create more than
one instance of config object.

By default, script will try to load all ``./config/*.yml`` and
``./config/settings/${APP_ENV}.yml`` configuration files.

Take note, that all variables defined in ``./config/*.yml`` files will
be overridden by variables from ``./config/settings/${APP_ENV}.yml``.

Also, ``./config/*.yml`` loaded in alphabetical order, so if you will
define variable VAR in ``additional_settings.yml`` it will be redefined
by VAR from ``settings.yml``.

Environment (development/stage/production etc)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your application use more than one environment, for example
``development`` and ``production``, you can specify what config file to
load by setting env variable

.. code:: python

    # before your application starts
    # export APP_ENV='production' or APP_ENV='production' python my_app.py 

    from app_settings import AppSettings

    cfg = AppSettings()

By default, if no ``APP_ENV`` is given, file
``./config/settings/development.yml`` will be loaded, that's why this
file is required.

Also it is possible to redefine name of variable.

.. code:: python

    # export TEST_ENV='production'

    from app_settings import AppSettings

    cfg = AppSettings(env_name='TEST_ENV')

Working with environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to redefine or set settings from environment variables.
AppSettings will read all env variables with ``SETTINGS`` prefix (by
default).

.. code:: yaml

    # settings.yml
    level1:
      redefined: 'redefined'
      not_redefined: 'not redefined'

.. code:: python

    # export SETTINGS__MY_VAR='test'
    # export SETTINGS__LEVEL1__REDEFINED='val'

    from app_settings import AppSettings

    cfg = AppSettings()
    print(cfg.my_var)  # 'test'
    print(cfg.level1.redefined)  # 'val'
    print(cfg.level1.not_redefined)  # 'not redefined'

You can setup your own prefix:

.. code:: python

    # export MYPREFIX__MY_VAR='test'
    # export MYPREFIX__LEVEL1__REDEFINED='val'

    from app_settings import AppSettings

    cfg = AppSettings(prefix='myprefix')
    print(cfg.my_var)  # 'test'
    print(cfg.level1.redefined)  # 'val'

Also it is possible to setup environment variable splitter (default:
``__``).

.. code:: python

    # export SETTINGS.MY_VAR='test'
    # export SETTINGS.LEVEL1.REDEFINED='val'

    from app_settings import AppSettings

    cfg = AppSettings(splitter='.')
    print(cfg.my_var)  # 'test'
    print(cfg.level1.redefined)  # 'val'

Config path
~~~~~~~~~~~

You can redefine default config path

.. code:: python

    from app_settings import AppSettings

    cfg = AppSettings(configs_path='my_config_path')

Run tests
---------

.. code:: bash

    cd app_settings
    python -m pytest -v --alluredir=./tests/results -n `nproc` --cov=app_settings --cov-config .coveragerc ./tests

TODO
----

1. Add reload feature
2. Do not raise error if setting not found in dictionary
3. Load all yml by mask ``./config/settings/${APP_ENV}.*.yml``
4. Add flag ``use_env``. If false, do not check env variables.
