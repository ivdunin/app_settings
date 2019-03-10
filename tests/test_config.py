import pytest
from re import search, compile


@pytest.mark.parametrize(
        'set_environ', [
            pytest.param('APP_ENV:development', id='Load development configs with default ENV variable name'),
            pytest.param('APP_ENV:production', id='Load production configs with default ENV variable name'),
            pytest.param('TEST_ENV:production', id='Load production configs with custom ENV variable name'),
            pytest.param(':development', id='Load development configs if ENV not set (default)'),
        ],
        indirect=['set_environ']
    )
def test_load_config_upon_env_name(clear_config_instance, set_environ, move_config_to_custom_dir):
    """ Test that proper version of config loaded """
    env_name, env_value = set_environ
    if env_name:
        cfg = clear_config_instance(env_name=env_name, configs_path=move_config_to_custom_dir)
    else:
        cfg = clear_config_instance(configs_path=move_config_to_custom_dir)

    assert cfg.common, 'Settings not loaded!'
    assert cfg.additional_settings, "Additional settings not loaded!"
    assert cfg.__getattr__(env_value), '{} config not loaded!'.format(env_value)
    assert env_value == cfg.current_env(), 'Incorrect config variable set!'


@pytest.mark.usefixtures("init_default_configs")
def test_load_config_from_default_location(clear_config_instance):
    """ Test that config correctly loaded from default location """
    cfg = clear_config_instance()

    assert cfg.common, 'Settings not loaded!'
    assert cfg.additional_settings, "Additional settings not loaded!"
    assert 'development' == cfg.current_env(), 'Incorrect config variable set!'


def test_load_config_when_no_default_location(clear_config_instance, caplog):
    """ Test that correctly handled case when no config dir """
    pattern = compile(r'Cannot find config dir:')

    caplog.clear()
    with pytest.raises(SystemExit):
        clear_config_instance(configs_path='fake')

    err_messages = []

    for rec in caplog.records:
        if rec.levelname == 'ERROR':
            err_messages.append(rec.message)

    res = search(pattern, ' '.join(err_messages))
    assert res, "Error message not found in: '{0}'".format(' '.join(err_messages))


def test_load_config_from_custom_location(clear_config_instance, set_environ, move_config_to_custom_dir):
    """ Test that config correctly loaded from custom location """
    env_name, env_value = set_environ
    cfg = clear_config_instance(env_name=env_name, configs_path=move_config_to_custom_dir)
    assert cfg.common, 'Settings not loaded!'
    assert cfg.additional_settings, "Additional settings not loaded!"
    assert cfg.__getattr__(env_value), '{} config not loaded!'.format(env_value)
    assert env_value == cfg.current_env(), 'Incorrect config variable set!'


def test_read_variables(clear_config_instance, move_config_to_custom_dir):
    """ Test get variable value by path """
    common_list = [
        "common-ba339256-f57e-4bb8-9914-bf3ec7bb1201",
        "common-9ead97e4-3ab9-4c5b-90ab-1caee3e44747",
        "common-88b3f0d0-3cad-4d58-8b36-1c6b5b2c68ae"
      ]

    multilevel = [
          "22 - 5080c0b2-5143-461c-a277-c670cce4d942",
          "22 - 2571baf8-e56d-46f2-bcf6-cee7a4a4caaa"
        ]

    cfg = clear_config_instance(configs_path=move_config_to_custom_dir)
    assert "common-774a3530-36df-11e9-b0b2-0028f8351bd7" == cfg.common.key1
    assert common_list == cfg.common.common_list
    assert "dev-774a3530-36df-11e9-b0b2-0028f8351bd7" == cfg.development.key1
    assert multilevel == cfg.multilevel.level2.level22


def test_redefine_variables_from_file(clear_config_instance, move_config_to_custom_dir):
    """ Test that variables from config/*.yml redefined by settings/*.yml variables """
    cfg = clear_config_instance(configs_path=move_config_to_custom_dir)
    assert ['3', '4'] == cfg.redefine.list, "settings.yml not redefined by settings/development.yml"
    assert "development.yml" == cfg.redefine.val, "settings.yml not redefined by settings/development.yml"
    assert "settings.yml" == cfg.yml_order, "additional_settings.yml not redefined by settings.yml"


@pytest.mark.parametrize(
        'set_environ', [
            pytest.param('SETTINGS__VAR__GET_FROM__ENV:environment value', id='Export SETTINGS__VAR__GET_FROM__ENV'),
        ],
        indirect=['set_environ']
    )
def test_redefine_variables_from_env(clear_config_instance, set_environ, move_config_to_custom_dir):
    """ Test that variables defined in file correctly redefined from ENV """
    _, val = set_environ
    cfg = clear_config_instance(configs_path=move_config_to_custom_dir)
    assert val == cfg.var.get_from.env


@pytest.mark.parametrize(
        'set_environ', [
            pytest.param('SETTINGS__CUSTOM__NEW__VAR:environment value', id='Export SETTINGS__CUSTOM__NEW__VAR'),
        ],
        indirect=['set_environ']
    )
def test_use_env_variables(clear_config_instance, set_environ, move_config_to_custom_dir):
    """ Test that variables from ENV line accessible in config (even if they not defined in config files) """
    _, val = set_environ
    cfg = clear_config_instance(configs_path=move_config_to_custom_dir)
    assert val == cfg.custom.new.var


@pytest.mark.parametrize(
        'set_environ', [
            pytest.param('MYPREFIX__CUSTOM__NEW__VAR:environment value', id='Export MYPREFIX__CUSTOM__NEW__VAR'),
        ],
        indirect=['set_environ']
    )
def test_redefine_variable_prefix(clear_config_instance, set_environ, move_config_to_custom_dir):
    """ Test that user can redefine variable prefix (default prefix SETTINGS) """
    _, env_val = set_environ
    cfg = clear_config_instance(prefix='myprefix', configs_path=move_config_to_custom_dir)
    assert env_val == cfg.custom.new.var


@pytest.mark.parametrize(
        'set_environ', [
            pytest.param('SETTINGS_._._CUSTOM_._._NEW_._._VAR:environment value',
                         id='Export SETTINGS_._._CUSTOM_._._NEW_._._VAR'),
        ],
        indirect=['set_environ']
    )
def test_redefine_variable_splitter(clear_config_instance, set_environ, move_config_to_custom_dir):
    """ Test that user can redefine variable splitter (default splitter "__") """
    _, env_val = set_environ
    cfg = clear_config_instance(splitter='_._._', configs_path=move_config_to_custom_dir)
    assert env_val == cfg.custom.new.var


def test_no_config_file(clear_config_instance, caplog):
    """ Test that FileNotFoundError correctly handled and logger.error message shown """
    pattern = compile(r'Config file "[./a-z]+" not found!'
                      r'\nPerhaps you set incorrect APP_ENV variable or file not exist!')

    caplog.clear()
    with pytest.raises(SystemExit):
        clear_config_instance(configs_path='../')

    err_messages = []

    for rec in caplog.records:
        if rec.levelname == 'ERROR':
            err_messages.append(rec.message)

    res = search(pattern, ' '.join(err_messages))
    assert res, "Error message not found in: '{0}'".format(' '.join(err_messages))


@pytest.mark.parametrize(
        'set_environ', [
            pytest.param('SETTINGS__USE_ENV:true', id='Turn off environment variables redefine'),
        ],
        indirect=['set_environ']
    )
def test_flag_use_env_off(clear_config_instance, set_environ, move_config_to_custom_dir):
    """ Test that variables not overriding when use_env=False """
    cfg = clear_config_instance(use_env=False, configs_path=move_config_to_custom_dir)
    assert 'false' == cfg.use_env
