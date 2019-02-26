import pytest

from os import environ


@pytest.mark.usefixtures("init_default_configs")
@pytest.mark.parametrize(
        'set_environ', [
            pytest.param('APP_ENV:development', id='Load development configs with default ENV variable name'),
            pytest.param('APP_ENV:production', id='Load production configs with default ENV variable name'),
            pytest.param('TEST_ENV:production', id='Load production configs with custom ENV variable name'),
            pytest.param(':development', id='Load development configs if ENV not set (default)'),
        ],
        indirect=['set_environ']
    )
def test_load_config_upon_env_name(clear_config_instance, set_environ):
    """ Test that proper version of config loaded """
    env_name, env_value = set_environ
    if env_name:
        cfg = clear_config_instance(env_name=env_name)
    else:
        cfg = clear_config_instance()

    assert cfg.common, 'Settings not loaded!'
    assert cfg.additional_settings, "Additional settings not loaded!"
    assert cfg.__getattr__(env_value), '{} config not loaded!'.format(env_value)
    assert env_value == cfg.current_env(), 'Incorrect config variable set!'


def test_load_config_from_custom_location(clear_config_instance, set_environ, move_config_to_custom_dir):
    """ Test that config correctly loaded from custom location """
    env_name, env_value = set_environ
    cfg = clear_config_instance(env_name=env_name, configs_path=move_config_to_custom_dir)
    assert cfg.common, 'Settings not loaded!'
    assert cfg.additional_settings, "Additional settings not loaded!"
    assert cfg.__getattr__(env_value), '{} config not loaded!'.format(env_value)
    assert env_value == cfg.current_env(), 'Incorrect config variable set!'


@pytest.mark.usefixtures("init_default_configs")
def test_read_variables(clear_config_instance):
    """ Test  """
    common_list = [
        "common-ba339256-f57e-4bb8-9914-bf3ec7bb1201",
        "common-9ead97e4-3ab9-4c5b-90ab-1caee3e44747",
        "common-88b3f0d0-3cad-4d58-8b36-1c6b5b2c68ae"
      ]

    multilevel = [
          "22 - 5080c0b2-5143-461c-a277-c670cce4d942",
          "22 - 2571baf8-e56d-46f2-bcf6-cee7a4a4caaa"
        ]

    cfg = clear_config_instance()
    assert "common-774a3530-36df-11e9-b0b2-0028f8351bd7" == cfg.common__key1
    assert common_list == cfg.common__common_list
    assert "dev-774a3530-36df-11e9-b0b2-0028f8351bd7" == cfg.development__key1
    assert multilevel == cfg.multilevel__level2__level22


@pytest.mark.usefixtures("init_default_configs")
def test_redefine_variables_from_file(clear_config_instance):
    cfg = clear_config_instance()
    assert ['3', '4'] == cfg.redefine__list
    assert "development.yml" == cfg.redefine__val


@pytest.mark.usefixtures("init_default_configs")
def test_redefine_variables_from_env(clear_config_instance):
    env_val = 'environment value'
    environ['SETTINGS__VAR__FROM__ENV'] = env_val
    cfg = clear_config_instance()
    assert env_val == cfg.var__from__env


@pytest.mark.usefixtures("init_default_configs")
def test_use_env_variables(clear_config_instance):
    env_val = 'environment value'
    environ['SETTINGS__CUSTOM__NEW__VAR'] = env_val
    cfg = clear_config_instance()
    assert env_val == cfg.custom__new__var
