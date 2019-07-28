from flask import Flask
import docker
import yaml

app = Flask(__name__)

client = docker.from_env()

# get list of services in docker-compose.yml except master scheduler
services = { k: v
    for k, v in yaml.safe_load(open("docker-compose.yml", 'r'))['services'].items()
    if k != 'master'
}

# get images from services
images = [ x['image'] for x in list(services.values())]

@app.route('/')
def index():
    return {
        'services': services,
        'api_spec': {
            'run_container': {
                'url' : '/run/<service_name>',
                'description': '작업 실행'
            },
            'stop_container': {
                'url' : '/stop/<service_name>',
                'description': '작업 정지'
            },
            'remove_container': {
                'url' : '/remove/<service_name>',
                'description': '작업 삭제'
            },
            'scale_container': {
                'url' : '/scale/<service_name>/<replicas>',
                'description': '작업 스케일 in-out'
            },
            'get_info': {
                'url' : '/info',
                'description': '작업 스케쥴링 상태 조회'
            },
            'get_resource': {
                'url' : '/resource',
                'description': '자원 사용 현황 조회'
            }
        }
    }

@app.route('/run/<service_name>')
def run_container(service_name):
    # validate the service_name whether it exists
    if service_name not in services.keys():
        return {
            'message': 'the specified service does not exist'
        }

    try:
        container = do_run_container(service_name)

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
            'message': e
        }

@app.route('/stop/<service_name>')
def stop_container(service_name):
    # validate the service_name whether it exists
    if service_name not in services.keys():
        return {
            'message': 'the specified service does not exist'
        }

    try:
        do_stop_containers(service_name)

        return {
            'message': 'Job {} is stopped.'.format(service_name),
            'service_name': service_name
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
            'message': e
        }

@app.route('/remove/<service_name>')
def remove_container(service_name):
    # validate the service_name whether it exists
    if service_name not in services.keys():
        return {
            'message': 'the specified service does not exist'
        }

    try:
        do_remove_containers(service_name)

        return {
            'message': 'Job {} is removed.'.format(service_name),
            'service_name': service_name
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

@app.route('/scale/<service_name>/<replicas>')
def scale_container(service_name, replicas):
    message = ''
    number = int(replicas)

    # validate the service_name whether it exists
    if service_name not in services.keys():
        return {
            'message': 'the specified service does not exist'
        }

    try:
        containers = get_containers_with_service_name(service_name)

        if len(containers) > number: # scale in
            do_stop_containers(service_name, number)
            message = '{} of Containers is/are stopped.'.format(len(containers) - number)
        elif len(containers) < number: # scale out
            for i in range(number - len(containers)):
                do_run_container(service_name)
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
    containers = {}

    try:
        # get list of containers only in docker-compose.yml
        for container in list(filter(lambda x: x.image.tags[0] in images, client.containers.list())):
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
            'message': e
        }

@app.route('/resource')
def get_resource():
    containers = {}

    try:
        # get list of containers only in docker-compose.yml
        for container in list(filter(lambda x: x.image.tags[0] in images, client.containers.list())):
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

def do_run_container(service_name):
    # get image_name of the service & run the container
    image_name = services[service_name]['image']
    container = client.containers.run(image_name, detach=True)
    return container

def do_stop_containers(service_name, number = 0):
    containers = get_containers_with_service_name(service_name)

    for container in containers[0:(len(containers) - number)]:
            container.stop()

def do_remove_containers(service_name):
    containers = get_containers_with_service_name(service_name)

    for container in containers:
            container.remove(force=True)

def get_containers_with_service_name(service_name):
    containers = []

    # get image_name of the service
    image_name = services[service_name]['image']

    # get a list of containers with same image
    for container in client.containers.list():
        if container.image.tags[0] == image_name:
            containers.append(container)

    return containers


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')