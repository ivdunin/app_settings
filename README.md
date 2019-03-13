# app_settings module
Simplify usage of YAML files for application configuration.

Inspired by Ruby Gem "config" https://github.com/railsconfig/config But not all features implemented yet.

## Usage example
Installation: `pip install app_settings`

Create sample app with following structure:
```bash
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
```
`AppSettings` -- singleton, so it is not possible to create more than one instance of config object.

By default, script will try to load all `./config/*.yml` and, if exist `./config/settings/${APP_ENV}*.yml` configuration files.

Take note, that all variables defined in `./config/*.yml` files will be overridden by variables from `./config/settings/${APP_ENV}.yml`.

Also, `./config/*.yml` loaded in alphabetical order, so if you will define variable VAR in `additional_settings.yml` it will be redefined by VAR from `settings.yml`.

If you have settings, which not depends on the environment, simply use `./config/{file name}.yml`; In case, when you need settings, which depends on the environment, use `./config/settings/{ENV}.yml`.

### Environment (development/stage/production etc)
If your application use more than one environment, for example `development` and `production`, you can specify what config file to load by setting env variable
```python
# before your application starts
# export APP_ENV='production' or APP_ENV='production' python my_app.py 

from app_settings import AppSettings

cfg = AppSettings()
```
By default, if no `APP_ENV` is given, file `./config/settings/development.yml` will be loaded, that's why this file is required.

Also it is possible to redefine name of variable.
```python
# export TEST_ENV='production'

from app_settings import AppSettings

cfg = AppSettings(env_name='TEST_ENV')
```

### Working with environment variables
It is possible to redefine or set settings from environment variables. AppSettings will read all env variables with `SETTINGS` prefix (by default).
```yaml
# settings.yml
level1:
  redefined: 'redefined'
  not_redefined: 'not redefined'
```

```python
# export SETTINGS__MY_VAR='test'
# export SETTINGS__LEVEL1__REDEFINED='val'

from app_settings import AppSettings

cfg = AppSettings()
print(cfg.my_var)  # 'test'
print(cfg.level1.redefined)  # 'val'
print(cfg.level1.not_redefined)  # 'not redefined'
```
You can setup your own prefix:
```python
# export MYPREFIX__MY_VAR='test'
# export MYPREFIX__LEVEL1__REDEFINED='val'

from app_settings import AppSettings

cfg = AppSettings(prefix='myprefix')
print(cfg.my_var)  # 'test'
print(cfg.level1.redefined)  # 'val'
```
Also it is possible to setup environment variable splitter (default: `__`). 
```python
# export SETTINGS.MY_VAR='test'
# export SETTINGS.LEVEL1.REDEFINED='val'

from app_settings import AppSettings

cfg = AppSettings(splitter='.')
print(cfg.my_var)  # 'test'
print(cfg.level1.redefined)  # 'val'
```

If you don't need to set/redefine settings from environment variables, use `use_env` flag.

```python
from app_settings import AppSettings
cfg = AppSettings(use_env=False)
```


### Config path
You can redefine default config path
```python
from app_settings import AppSettings

cfg = AppSettings(configs_path='my_config_path')
```

## Run tests
```bash
cd app_settings
python -m pytest -v --alluredir=./tests/results -n `nproc` --cov=app_settings --cov-config .coveragerc ./tests
```

## TODO
1. Add reload feature
2. Do not raise error if setting not found in dictionary
