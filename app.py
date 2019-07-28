from flask import Flask
import docker

app = Flask(__name__)

@app.route('/')
def index():
    return {
        'run_container': {
            'url' : '/run/<path:image_name>',
            'description': '컨테이너 실행'
        },
        'stop_container': {
            'url' : '/stop/<container_id>',
            'description': '컨테이너 정지'
        },
        'remove_container': {
            'url' : '/remove/<container_id>',
            'description': '컨테이너 삭제'
        },
        'scale_container': {
            'url' : '/scale/<container_id>/<replicas>',
            'description': '컨테이터 스케일 in-out'
        },
        'get_info': {
            'url' : '/info',
            'description': '컨테이너 스케쥴링 상태 조회'
        },
        'get_resource': {
            'url' : '/resource',
            'description': '자원 사용 현황 조회'
        }
    }

@app.route('/run/<path:image_name>')
def run_container(image_name):
    client = docker.from_env()

    try:
        container = client.containers.run(image_name, detach=True)

        return {
            'message': 'Container {} ({}) is started.'.format(container.short_id, container.image.tags[0]),
            'container_id': container.short_id
        }
    except docker.errors.ContainerError:
        return {
            'message': 'the container exits with a non-zero exit code and detach is False.'
        }
    except docker.errors.ImageNotFound:
        return {
            'message': 'the specified image does not exist'
        }
    except docker.errors.APIError:
        return {
            'message': 'the server returns an error'
        }
    except Exception as e:
        return {
            'message': 'error'
        }

@app.route('/stop/<container_id>')
def stop_container(container_id):
    client = docker.from_env()

    try:
        client.containers.get(container_id).stop()

        return {
            'message': 'Container {} is stopped.'.format(container_id),
            'container_id': container_id
        }
    except docker.errors.NotFound:
        return {
            'message': 'the container does not exist'
        }
    except docker.errors.APIError:
        return {
            'message': 'the server returns an error'
        }
    except Exception as e:
        return {
            'message': 'error'
        }

@app.route('/remove/<container_id>')
def remove_container(container_id):
    client = docker.from_env()

    try:
        client.containers.get(container_id).remove(force=True)

        return {
            'message': 'Container {} is removed.'.format(container_id),
            'container_id': container_id
        }
    except docker.errors.NotFound:
        return {
            'message': 'the container does not exist'
        }
    except docker.errors.APIError:
        return {
            'message': 'the server returns an error'
        }
    except Exception as e:
        return {
            'message': 'error'
        }

@app.route('/scale/<container_id>/<replicas>')
def scale_container(container_id, replicas):
    client = docker.from_env()
    message = ''
    containers = []
    number = int(replicas)

    try:
        # get image data of container for scaling
        image_name = client.containers.get(container_id).image.tags[0]

        # get a list of containers with same image
        for container in client.containers.list():
            if container.image.tags[0] == image_name:
                containers.append(container)

        if len(containers) > number: # scale in
            for container in containers[0:(len(containers) - number)]:
                container.stop()
            message = '{} of Containers is/are stopped.'.format(len(containers) - number)
        elif len(containers) < number: # scale out
            for i in range(number - len(containers)):
                client.containers.run(image_name, detach=True)
            message = '{} of Containers is/are started.'.format(number - len(containers))
        else:
            message = 'Desired # of Containers is/are already running.'

        return {
            'message': message
        }
    except docker.errors.APIError:
        return {
            'message': 'the server returns an error'
        }
    except Exception as e:
        return {
            'message': 'error'
        }

@app.route('/info')
def get_info():
    client = docker.from_env()
    containers = {}

    try:
        for container in client.containers.list():
            containers[container.short_id] = {
                'image': container.image.tags[0],
                'status': container.status,
                'created': container.attrs['Created'],
                'name': container.attrs['Name']
            }

        return containers
    except docker.errors.APIError:
        return {
            'message': 'the server returns an error'
        }
    except Exception as e:
        return {
            'message': 'error'
        }

@app.route('/resource')
def get_resource():
    client = docker.from_env()
    containers = {}

    try:
        for container in client.containers.list():
            containers[container.short_id] = container.stats(stream=False)

        return containers
    except docker.errors.APIError:
        return {
            'message': 'the server returns an error'
        }
    except Exception as e:
        return {
            'message': 'error'
        }


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')