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
        settings.yml  # at least one *.yml file required
        additional_settings.yml
        /settings  # use this only in case if you need different settings for your environments
          production.yml
          production.db.yml
          development.yml
          development.db.yml   

``AppSettings`` -- singleton, so it is not possible to create more than
one instance of config object.

By default, script will try to load all ``./config/*.yml`` and, if exist
``./config/settings/${APP_ENV}*.yml`` configuration files.

Take note, that all variables defined in ``./config/*.yml`` files will
be overridden by variables from ``./config/settings/${APP_ENV}.yml``.

Also, ``./config/*.yml`` loaded in alphabetical order, so if you will
define variable VAR in ``additional_settings.yml`` it will be redefined
by VAR from ``settings.yml``.

If you have settings, which not depends on the environment, simply use
``./config/{file name}.yml``; In case, when you need settings, which
depends on the environment, use ``./config/settings/{ENV}.yml``.

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

If you don't need to set/redefine settings from environment variables,
use ``use_env`` flag.

.. code:: python

    from app_settings import AppSettings
    cfg = AppSettings(use_env=False)

Suppress KeyError exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case, if you don't want to receive KeyError exception if key not
defined in file, you can use ``raise_error`` flag. By default: True

.. code:: python

    from app_settings import AppSettings
    cfg = AppSettings(raise_error=False)

    key = cfg.this_value_not_exist  # key == None

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

Sample usage for tests
~~~~~~~~~~~~~~~~~~~~~~

Run these commands to create sample files structure

.. code:: bash

    $ cd <your project dir> 
    $ mkdir -p config/settings && \ 
        touch config/settings.yml && \
        touch config/settings/{production.yml,testing.yml} && \
        echo "implicity_wait: 5" > config/settings.yml && \
        echo 'search_text: "production environment"' > config/settings/production.yml && \
        echo 'search_text: "testing environment"' > config/settings/testing.yml
    $ touch test_with_app_settings.py

Install all python requirements:

.. code:: bash

    pip install selenium pytest app_settings

Copy code to ``test_with_app_settings.py``

.. code:: python

    ### Example, don't use it in your code
    import os
    os.environ['TEST_ENV'] = 'production'
    ### example

    import pytest
    from app_settings import AppSettings
    from selenium import webdriver


    @pytest.fixture(scope='session')
    def settings():
        cfg = AppSettings(env_name='TEST_ENV')
        return cfg


    @pytest.fixture
    def browser(settings):
        driver = webdriver.Chrome()
        driver.implicitly_wait(settings.implicity_wait)
        yield driver
        driver.close()


    def test_example(browser, settings):
        browser.get("https://ya.ru")
        search_field = browser.find_element_by_id('text')
        search_field.send_keys(settings.search_text)  # depending on env
        search_button = browser.find_element_by_tag_name('button')
        search_button.click()
        browser.find_elements_by_css_selector("div ul li")

TODO
----

1. Add reload feature

