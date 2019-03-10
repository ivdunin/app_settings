#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 Dunin Ilya.
""" Module description """

import pytest

from distutils.dir_util import copy_tree, remove_tree
from os import path, makedirs, environ, chdir, getcwd
from tempfile import mkdtemp

from app_settings.app_settings import AppSettings, Singleton, DEFAULT_ENV

CURRENT_DIR = path.dirname(__file__)

# TODO test empty config files


@pytest.fixture
def clear_config_instance():
    """ New singleton instance """
    Singleton._instances = {}
    yield AppSettings


@pytest.fixture
def init_default_configs():
    """ Create default directory for configs and config files """
    default_path = path.join(CURRENT_DIR, '..', 'app_settings', 'config')
    if not path.exists(default_path):
        makedirs(default_path)

    old_cur_dir = getcwd()
    chdir(path.dirname(default_path))

    copy_tree(path.join(CURRENT_DIR, 'data'), default_path)

    yield

    chdir(old_cur_dir)
    remove_tree(default_path)


@pytest.fixture
def move_config_to_custom_dir(request):
    """ Move configs to custom location """
    try:
        custom_path = request.param
    except AttributeError:
        custom_path = path.join(mkdtemp(), 'config')

    print('create dir: {}'.format(custom_path))

    if not path.exists(custom_path):
        makedirs(custom_path)

    copy_tree(path.join(CURRENT_DIR, 'data'), custom_path)

    yield custom_path

    remove_tree(custom_path)


@pytest.fixture
def set_environ(request):
    """ Set ENV variable """
    try:
        env_name, env_value = request.param.split(':')
    except AttributeError:
        env_name, env_value = DEFAULT_ENV, 'development'

    if env_name:
        environ[env_name] = env_value

    yield env_name, env_value

    if env_name:
        del environ[env_name]
