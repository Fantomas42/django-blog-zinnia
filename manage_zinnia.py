import subprocess
import uuid
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('action', help='Action to perform.', choices=['build-docs', 'start-demo'])
parser.add_argument('--port', help='Binding Port for Demo Site', required=False)
parser.add_argument('--workers', help='Number of Workers for Demo Site', required=False)

args = parser.parse_args()


def start_demo_site(port, workers):
    try:
        process = subprocess.run(
            f'SECRET_KEY={uuid.uuid4()} gunicorn demo.wsgi -w {workers} -b 127.0.0.1:{port}',
            shell=True
        )
    except:
        process.kill()


def build_docs():
    subprocess.run(
        'sphinx-build ./docs/ ./dist/docs',
        shell=True
    )


if __name__ == '__main__':
    action = args.action
    if action == 'build-docs':
        build_docs()
    elif action == 'start-demo':
        port = args.port
        workers = args.workers
        start_demo_site(port, workers)
