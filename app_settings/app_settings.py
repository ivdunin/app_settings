#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" YAML Config Module """

from glob import glob
from json import dumps
from logging import getLogger, basicConfig, INFO
from os import path, environ, getcwd

from yaml import load, FullLoader

g_logger = getLogger(__name__)
basicConfig(level=INFO,
            format='%(asctime)s %(module)s:%(lineno)d [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')


DEFAULT_ENV = 'APP_ENV'
DEFAULT_ENV_PREFIX = 'SETTINGS'
DEFAULT_SPLITTER = '__'
DEFAULT_ENV_VALUE = 'development'


class CustomDict(dict):
    """ Dict which allow to access to dict values using dot, e.g. my_dict.key.key1 instead my_dict['key']['key1'] """
    def __getattr__(self, item):
        val = self[item]
        if isinstance(val, dict):
            return CustomDict(val)
        else:
            return val


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AppSettings(metaclass=Singleton):
    """ Config class (singleton) """
    def __init__(self, **kwargs):
        self.__config = CustomDict()

        try:
            self._env_name = kwargs.get('env_name', DEFAULT_ENV).upper()
            self._env_value = environ[self._env_name]
        except KeyError:
            self._env_value = kwargs.get('default_env_value', DEFAULT_ENV_VALUE)

        g_logger.info(f'Config initialized! Environment variable: {self._env_name}={self._env_value}')

        config_location = kwargs.get('configs_path', path.join(getcwd(), 'config'))
        self._env_prefix = kwargs.get('prefix', DEFAULT_ENV_PREFIX).upper()
        self._env_splitter = kwargs.get('splitter', DEFAULT_SPLITTER)
        self._raise_error = kwargs.get('raise_error', True)

        configs = glob(path.join(config_location, '*.yml'))

        if configs:
            for cfg_file in sorted(configs):
                self._load_config(cfg_file)
        else:
            g_logger.error('Cannot find config dir/or config files: %s', path.join(config_location, '*.yml'))
            exit(1)

        env_configs = glob(path.join(config_location, 'settings', '{}*.yml'.format(self._env_value)))

        if env_configs:
            for yml_file in sorted(env_configs):
                self._load_config(yml_file)
        else:
            g_logger.info(f'"{self._env_value}*.yml" configs not found!')

        if kwargs.get('use_env', True):
            self._redefine_variables()

    def __repr__(self):
        return dumps(self.__config, sort_keys=True, indent=2)

    def _load_config(self, config_file):
        """ Load yml config from file """
        g_logger.debug('Load config file: %s', config_file)
        with open(config_file) as fp:
            cfg = load(fp, Loader=FullLoader)
            if cfg:
                self.__config.update(cfg)

    def _redefine_variables(self):
        """ Search for ENV variables with prefix and add them into config dict """
        for env_name in [key for key in environ.keys() if key.startswith(self._env_prefix)]:
            env_val = environ[env_name]
            g_logger.debug(f'Found env variable: {env_name} = {env_val}')
            keys = env_name.\
                replace(self._env_prefix, '').\
                lstrip(self._env_splitter).\
                lower().\
                split(self._env_splitter)
            keys.reverse()
            self._set_config_value(keys, env_val, self.__config)

    def __getattr__(self, item):
        if self._raise_error:
            return self.__config.__getattr__(item)
        else:
            try:
                return self.__config.__getattr__(item)
            except KeyError:
                g_logger.warning(f'Key "{item}" not found!')
                return

    def _set_config_value(self, keys, value, cfg=None):
        """ Set config value in config dict """
        g_logger.debug("Set value '%s' for key: %s", value, keys)
        key = keys.pop()
        if keys:
            self._set_config_value(keys, value, cfg.setdefault(key, {}))
        else:
            cfg[key] = value

    @property
    def current_env(self):
        """ Get env of loaded config """
        return self._env_value
