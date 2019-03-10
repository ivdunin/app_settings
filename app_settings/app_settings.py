#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" YAML Config Module """

from json import dumps
from logging import getLogger
from os import path, environ, listdir, getcwd
from yaml import load

g_logger = getLogger(__name__)


DEFAULT_ENV = 'APP_ENV'
DEFAULT_ENV_PREFIX = 'SETTINGS'
DEFAULT_SPLITTER = '__'


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
            self._env_value = 'development'

        g_logger.info('Config initialized! Environment variable: %s', self._env_value)

        config_location = kwargs.get('configs_path', path.join(getcwd(), 'config'))
        self._env_prefix = kwargs.get('prefix', DEFAULT_ENV_PREFIX).upper()
        self._env_splitter = kwargs.get('splitter', DEFAULT_SPLITTER)

        try:
            for cfg_file in sorted(listdir(config_location)):
                if path.isfile(path.join(config_location, cfg_file)) and cfg_file.lower().endswith('.yml'):
                    self._load_config(path.join(config_location, cfg_file))

            self._load_config(path.join(config_location, 'settings', '{}.yml'.format(self._env_value)))
        except FileNotFoundError as e:
            g_logger.error('Cannot find config dir: %s', e)
            exit(1)

        if kwargs.get('use_env', True):
            self._redefine_variables()

    def __repr__(self):
        return dumps(self.__config, sort_keys=True, indent=2)

    def _load_config(self, config_file):
        """ Load yml config from file """
        g_logger.debug('Load config file: %s', config_file)
        try:
            with open(config_file) as fp:
                cfg = load(fp)
                if cfg:
                    self.__config.update(cfg)
        except FileNotFoundError:
            g_logger.error('Config file "%s" not found!'
                           '\nPerhaps you set incorrect %s variable or file not exist!', config_file, self._env_name)
            exit(1)

    def _redefine_variables(self):
        """ Search for ENV variables with prefix and add them into config dict """
        for env_name in [key for key in environ.keys() if key.startswith(self._env_prefix)]:
            env_val = environ[env_name]
            g_logger.debug('Found env variable: %s = %s', env_name, env_val)
            keys = env_name.\
                replace(self._env_prefix, '').\
                lstrip(self._env_splitter).\
                lower().\
                split(self._env_splitter)
            keys.reverse()
            self._set_config_value(keys, env_val, self.__config)

    def __getattr__(self, item):
        return self.__config.__getattr__(item)

    def _set_config_value(self, keys, value, cfg=None):
        """ Set config value in config dict """
        g_logger.debug("Set value '%s' for key: %s", value, keys)
        key = keys.pop()
        if keys:
            self._set_config_value(keys, value, cfg.setdefault(key, {}))
        else:
            cfg[key] = value

    def current_env(self):
        """ Get env of loaded config """
        return self._env_value
