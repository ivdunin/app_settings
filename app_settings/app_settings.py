#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" YAML Config Module """

from json import dumps
from logging import getLogger
from os import path, environ, listdir
from yaml import load

g_logger = getLogger(__name__)

# TODO: remove all f strings
# TODO: custom splitter ( __ )
# TODO: add to settings all vars with special format SOME_WORD__VAR1, SOME_WORD__VAR2
# TODO: test that variable values correctly redefined from common and production/development


DEFAULT_ENV = 'APP_ENV'
DEFAULT_CONFIGS_PATH = path.join(path.dirname(__file__), 'config')
DEFAULT_ENV_PREFIX = 'SETTINGS'


# class DictConfig(dict):
#     def __getattr__(self, item):
#         return self[item]


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AppSettings(metaclass=Singleton):
    """ Config class """
    def __init__(self, **kwargs):
        self.__config = {}

        try:
            self._env_name = kwargs.get('env_name', DEFAULT_ENV).upper()
            self._env_value = environ[self._env_name]
        except KeyError:
            self._env_value = 'development'

        g_logger.info('Config initialized! Environment variable: %s', self._env_value)

        config_location = kwargs.get('configs_path', DEFAULT_CONFIGS_PATH)

        for cfg_file in listdir(config_location):
            if path.isfile(path.join(config_location, cfg_file)) and cfg_file.lower().endswith('.yml'):
                self._load_config(path.join(config_location, cfg_file))

        self._load_config(path.join(config_location, 'settings', '{}.yml'.format(self._env_value)))

        # self._redefine_variables()

    def __repr__(self):
        return dumps(self.__dict__, sort_keys=True, indent=2)

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

    # def _redefine_variables(self):
    #     for env_name, env_val in environ.items():
    #         if env_name.startswith(DEFAULT_ENV_PREFIX):
    #             print(env_name, env_val)

    def __getattr__(self, item):
        g_logger.debug('Get attribute value: %s', item)
        keys = item.split('__')
        keys.reverse()
        val = self._get_config_value(keys, self.__config)
        if val is not None:
            try:
                # redefine variable only if exist in settings
                val = environ[item.upper()]
                g_logger.warning('Redefine %s from env variables.', item)  # TODO: move redefining to load function
                return val
            except KeyError:
                return val
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def _get_config_value(self, keys, cfg=None):
        """ Get value

        :param keys: keys list
        :param cfg: config
        :return: config value
        """
        g_logger.debug('Keys: %s', keys)
        key = keys.pop()
        if key in cfg:
            if keys:
                return self._get_config_value(keys, cfg.get(key))
            else:
                return cfg.get(key)
        else:
            return None

    def current_env(self):
        """ Get env of loaded config """
        return self._env_value
