import logging
import os
import yaml
import pytest
from main import run_gcloud_command

def pytest_collection_modifyitems(session, config, items):
    prefix = os.getenv('PREFIX')
    for item in items:
        logging.debug(f"Parsing {item.callspec}")
        for step in item.callspec.params.get('steps', {}):
            command = f"{step.get('command').replace('{{ prefix }}', prefix)}"
            logging.debug(f"Updating prefix for command={step.get('command')}")
            step.update(command=command)


@pytest.hookimpl
def pytest_runtest_teardown(item, nextitem):
    for step in item.callspec.params.get('steps', {}):
        if 'teardown' in step:
            prefix = os.getenv('PREFIX')
            teardown_command = f"{step.get('teardown').replace('{{ prefix }}', prefix)}"
            logging.debug(f"Updating prefix for teardown command={step.get('teardown')}")
            run_gcloud_command(teardown_command)
        else:
            logging.debug("Nothing done. No teardown command available")


@pytest.hookimpl
def pytest_generate_tests(metafunc):
    if "name" in metafunc.fixturenames and "steps" in metafunc.fixturenames:
        test_folder = os.path.join(os.getcwd(), "test_cases")
        test_cases = generate_test_cases(test_folder)
        metafunc.parametrize("name,steps", test_cases)

def generate_test_cases(folder_path):
    logging.debug(f"Generating test cases from (folder_path)")
    test_cases = []
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(".yaml"):
                filepath = os.path.join(root, filename)
                logging.debug(f"Processing {filepath}")
                with open(filepath, "r") as file:
                    data = yaml.safe_load(file)
                    for key, value in data.items():
                        marks = [getattr(pytest.mark, mark) for mark in value.get("tags", [])]
                        test_cases.append(pytest.param(key, value.get("steps"), marks=marks))

    return test_cases

