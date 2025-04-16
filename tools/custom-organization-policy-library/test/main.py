import os
import logging
import shlex
import logging
import shutil
import subprocess

def sanitize_command(command):
    command[0] = shutil.which("gcloud") 
    command.extend(["--format", "json"])
    command.extend(["--quiet"])
    command.extend(["project", os.getenv('PROJECT_ID')])
    return command


def run_gcloud_command(command):
    command = shlex.split(command)
    command = sanitize_command(command)
    logging.debug(f"Executing command {command}")
    response = subprocess.run(command, capture_output=True) 
    return response


def test_canary(name, steps):
    logging.debug(f"Running test {name}")
    for step in steps:
        command = shlex.split(step.get("command"))
        if command[0] == 'gcloud':
            output = run_gcloud_command(step.get("command"))
        else:
            logging.fatal(f"Command {command[0]} is not supported")
            exit(1)
        
        result = parse_output(step, output)
        assert result == True


def parse_output(step, output):
    stdout = output.stdout.decode("utf-8")
    stderr = output.stderr.decode("utf-8")
    logging.debug(f"stdout: {stdout}")
    logging.debug(f"stderr: {stderr}")

    if step.get("exitcode", 0) != output.returncode:
        logging.debug(f"Expected exitcode: (step.get('exitcode', 0)), got: {output.returncode}")
        return False

    if step.get('stdout', '') not in stdout:
        logging.debug(f"Expected stdout substring: {step.get('stdout', '')}, not found in: {stdout}")
        return False

    if step.get('stderr', '') not in stderr:
        logging.debug(f"Expected stderr substring: {step.get('stderr', '')}, not found in: {stderr}")
        return False
    return True
