import argparse
import glob
import logging
import os
import subprocess
import sys

file_formatter = logging.Formatter("[%(asctime)s/%(levelname)5.5s]  %(message)s")
stream_formatter = logging.Formatter("[%(asctime)s/%(levelname)5.5s]  %(message)s", datefmt="%H:%M:%S")
file_handler = logging.FileHandler("build.log")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
stream_handler.setLevel(logging.DEBUG)

log = logging.getLogger(__name__)

log.addHandler(file_handler)
log.addHandler(stream_handler)
log.setLevel(logging.DEBUG)


def build_dev(args):
    log.info("Building dev environment")

    try:
        subprocess.run("poetry --version", shell=True, check=True)
    except Exception as e:
        log.error(f"Poetry not found: {e}")
        subprocess.run(f"{sys.executable} -m pip install --upgrade pip poetry", shell=True)

    cmds = [
        f"poetry env use {sys.executable}",
        f"poetry install -v --with=dev,test --all-extras --sync",
        f"poetry run pre-commit install",
    ]
    log.info("Installing requirements")
    for cmd in cmds:
        log.debug(f"Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    log.info("Call 'poetry shell' to enter the virtual environment")


def build_wheels(args):
    log.info("Building wheels")

    subprocess.run(f"poetry build", shell=True, check=True)
    wheels = glob.glob(os.path.join("dist", "*.whl"))
    log.info(f"Found {len(wheels)} wheels")
    for w in wheels:
        log.info(f"- {w}")

    for w in wheels:
        log.info(f"Compiling {w}")
        subprocess.run(f"{sys.executable} -m pyc_wheel {w}", shell=True, check=True)


def run_tests(args):
    # test_dir = os.path.abspath(args.test_dir)

    # if not os.path.isdir(test_dir):
    #     os.makedirs(test_dir)

    modules = glob.glob(os.path.join(os.path.dirname(__file__), "rep_*", "setup.py"))
    modules = [os.path.relpath(os.path.dirname(m)) for m in modules]

    modules_str = " ".join(modules)

    return_code = 0
    try:
        base_cmd = f"{sys.executable} -m pytest -v --durations=10 --timeout={args.test_timeout}\
             --junitxml {args.test_results} -rf"
        if args.max_fail:
            base_cmd += f" --maxfail={args.max_fail}"
        if args.no_traceback:
            base_cmd += " --tb=no"
        base_cmd += f" --reruns={args.reruns} --reruns-delay={args.reruns_delay}"
        p = subprocess.run(f"{base_cmd} {modules_str}", shell=True, env=os.environ)
        return_code = p.returncode
    finally:
        return return_code


if __name__ == "__main__":
    log.debug(f"Using python at: {sys.executable}")
    # if not hasattr(sys, "base_prefix") or sys.base_prefix == sys.prefix:
    #     log.info(f"This script should only be ran inside of a virtual env")
    #     sys.exit(1)

    test_directory = "test_run"

    parser = argparse.ArgumentParser(description="Build and test")
    parser.set_defaults(func=build_dev)
    parser.add_argument("--revision", default="dev", help="Set the revision")
    parser.add_argument("--short-revision", default="dev", help="Set short revision")
    parser.add_argument("--branch", default="dev", help="Set branch")
    commands = parser.add_subparsers(title="commands", description="valid commands", dest="cmd")

    dev = commands.add_parser("dev")
    dev.set_defaults(func=build_dev)

    tests = commands.add_parser("tests")
    tests.set_defaults(func=run_tests)
    tests.add_argument(
        "-o",
        "--test_dir",
        default=test_directory,
        help="Directory to switch to before running tests",
    )
    tests.add_argument(
        "--test_results",
        default=os.path.join(test_directory, "test_results.xml"),
        help="Where to dump test results",
    )
    tests.add_argument("-t", "--test_timeout", default=30, help="Time after which to kill the test, in seconds")
    tests.add_argument(
        "-x",
        "--max_fail",
        type=int,
        default=0,
        help="Number of tests that are allowed to fail before stopping",
    )
    tests.add_argument(
        "-T",
        "--no_traceback",
        action="store_true",
        help="Don't print tracebacks at end of a test run",
    )
    tests.add_argument("-reruns", default=3, help="Max number of reruns for failed tests")
    tests.add_argument("-reruns-delay", default=3, help="Delay between reruns")

    wheels = commands.add_parser("wheels")
    wheels.set_defaults(func=build_wheels)

    args = parser.parse_args()
    result = args.func(args)
    if isinstance(result, int):
        sys.exit(result)
