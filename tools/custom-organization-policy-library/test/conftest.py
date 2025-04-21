import logging
import os
import yaml
import pytest
from main import run_gcloud_command

TEST_CASES_DIR = os.path.join(os.path.dirname(__file__), "test_cases")


def pytest_sessionstart(session):
    """Check for essential setup before starting the session."""
    if not os.path.isdir(TEST_CASES_DIR):
        pytest.exit(f"Test case directory not found: {TEST_CASES_DIR}", returncode=1)
    if not os.getenv('PREFIX'):
        pytest.exit("Environment variable 'PREFIX' is not set. It is required for test execution.", returncode=1)


def pytest_collection_modifyitems(session, config, items):
    """
    Modify collected tests to inject the PREFIX into command strings.
    """
    prefix = os.getenv('PREFIX')
    for item in items:
        if 'steps' in getattr(item, 'callspec', {}).params:
            logging.debug("Processing pytest item: %s", item.nodeid)
            steps = item.callspec.params.get('steps', [])
            for step in steps:
                identifier = None
                identifier_template = step.get('identifier')
                if identifier_template is not None:
                    if '{{ prefix }}' in identifier_template and prefix is None:
                        logging.error("PREFIX environment variable is None during identifier update. This shouldn't happen")
                    identifier = identifier_template.replace('{{ prefix }}', prefix)

                command_template = step.get('command')
                if command_template is None:
                    continue

                if '{{ prefix }}' in command_template and prefix is not None:
                    command = command_template.replace('{{ prefix }}', prefix)

                if '{{ identifier }}' in command_template and identifier is not None:
                    command = command_template.replace('{{ identifier }}', identifier)

                logging.debug("Updating prefix and identifier for command to %s", command)
                step.update(command=command)

@pytest.hookimpl
def pytest_runtest_teardown(item, nextitem):
    """
    Execute teardown commands defined in test steps after the test runs.
    """
    logging.debug("Running teardown check for item: %s", item.nodeid)
    prefix = os.getenv('PREFIX')
    steps = item.callspec.params.get('steps', [])
    for step in steps:
        identifier = None
        identifier_template = step.get('identifier')
        if identifier_template is not None:
            if '{{ prefix }}' in identifier_template and prefix is None:
                logging.error("PREFIX environment variable is None during identifier update. This shouldn't happen")
            identifier = identifier_template.replace('{{ prefix }}', prefix)

        teardown_template = step.get('teardown_command')
        if teardown_template is None:
            logging.debug("No 'teardown' key found in step for %s.", item.nodeid)
            continue
        
        logging.debug("Found teardown command template: %s", teardown_template)

        teardown_command = teardown_template
        if '{{ prefix }}' in teardown_template and prefix is not None:
            teardown_command = teardown_command.replace('{{ prefix }}', prefix)

        if '{{ identifier }}' in teardown_template and identifier is not None:
            teardown_command = teardown_command.replace('{{ identifier }}', identifier)

        logging.info("Executing teardown command %s", teardown_command)
        try:
            run_gcloud_command(teardown_command)
            logging.debug("Teardown command executed successfully.")
        except Exception as e:
            logging.error(
                "Teardown command failed for command: %s\nError: %s",
                teardown_command,
                e)

@pytest.hookimpl
def pytest_generate_tests(metafunc):
    """
    Generate parametrized tests from YAML files found in TEST_CASES_DIR.
    """
    if "name" in metafunc.fixturenames and "steps" in metafunc.fixturenames:
        logging.debug("Generating tests for %s from directory: %s", metafunc.function.__name__, TEST_CASES_DIR)
        test_cases = generate_test_cases(TEST_CASES_DIR, metafunc)
        try:
            metafunc.parametrize("name,steps", test_cases)
        except Exception as e:
            logging.error("Failed to parametrize %s: %s", metafunc.function.__name__, e, exc_info=True)
            pytest.fail(f"Error during parametrization of {metafunc.function.__name__}: {e}")


def generate_test_cases(folder_path, metafunc):
    """
    Walks a folder, parses YAML files, and yields pytest.param objects.
    """
    logging.debug("Scanning for YAML test cases in: %s", folder_path)

    test_cases = []
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith((".yaml", ".yml")):
                filepath = os.path.join(root, filename)
                logging.debug("Processing YAML file: %s", filepath)
                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        data = yaml.safe_load(file)
                        setup = data.get("setup", {})
                        logging.info("Retrieving common information: %s", setup)
                        for key, value in data.items():
                            if key == "setup": 
                                continue
                            markers = value.get("markers", [])
                            marks = [getattr(pytest.mark, mark)
                                     for mark in markers]
                            test_cases.append(pytest.param(key, value.get("steps"), 
                                                           marks=marks))
                except yaml.YAMLError as e:
                    logging.error("Error parsing YAML file %s: %s", filepath, e)
                    continue
                except Exception as e:
                    logging.error("Unexpected error processing file %s: %s", 
                                  filepath, e, exc_info=True)
                    continue
    return test_cases
