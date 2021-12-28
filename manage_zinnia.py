from argparse import ArgumentParser
import subprocess

parser = ArgumentParser()
parser.add_argument('action', help='Action to perform.', choices=['build-docs'])
args = parser.parse_args()


def build_docs():
    subprocess.run(
        'sphinx-build ./docs/ ./dist/docs',
        shell=True
    )


if __name__ == '__main__':
    action = args.action
    if action == 'build-docs':
        build_docs()
