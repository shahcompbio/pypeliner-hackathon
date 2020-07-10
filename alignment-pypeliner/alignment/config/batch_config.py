import collections
import logging
import os

import yaml
from alignment.utils import helpers


class folded_unicode(unicode):
    pass


class literal_unicode(unicode):
    pass


def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)


def override_config(config, override):
    def update(d, u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                d[k] = update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    if not override:
        return config

    cfg = update(config, override)

    return cfg


def get_vm_size_azure(numcores, memory, tasks_per_node):
    numcores = tasks_per_node * numcores
    memory = memory * tasks_per_node

    if numcores <= 2 and memory <= 16:
        return "STANDARD_E2_V3"
    elif numcores <= 4 and memory <= 32:
        return "STANDARD_E4_V3"
    elif numcores <= 8 and memory <= 64:
        return "STANDARD_E8_V3"
    else:
        # max 16 cores
        return "STANDARD_E16_V3"


def get_vm_image_id():
    imagename = 'wgs-prod-bigdisk-v1-image'

    subscription = os.environ.get("SUBSCRIPTION_ID", "id-missing")
    resource_group = os.environ.get("RESOURCE_GROUP", "wgscompute")
    imageid = ['subscriptions', subscription, 'resourceGroups',
               resource_group, 'providers', 'Microsoft.Compute',
               'images', imagename]
    imageid = '/'.join(imageid)
    imageid = '/' + imageid
    return imageid


def generate_standard_pool(reference):
    autoscale_formula = generate_autoscale_formula(4, False)

    vm_commands = create_vm_commands()

    vm_image = get_vm_image_id()
    node_sku = "batch.node.ubuntu 18.04"

    task_start_commands = get_compute_start_commands(vm_image)
    task_finish_commands = get_compute_finish_commands()

    poolname = "wgs_{}{}_v3".format(reference, 'standard')

    pooldata = {
        "pool_vm_size": get_vm_size_azure(1, 8, 4),
        "cpus_per_task": 1,
        'mem_per_task': 8,
        "disk_per_task": 200,
        'dedicated': False,
        'node_resource_id': vm_image,
        'node_os_publisher': 'Canonical',
        'node_os_offer': 'UbuntuServer',
        'node_os_sku': node_sku,
        'data_disk_sizes': None,
        'max_tasks_per_node': 4,
        'auto_scale_formula': autoscale_formula,
        'create_vm_commands': vm_commands,
        'start_resources': None,
        'compute_start_commands': task_start_commands,
        'compute_finish_commands': task_finish_commands
    }

    return {poolname: pooldata}


def generate_multicore_pool(reference):
    autoscale_formula = generate_autoscale_formula(4, False)

    vm_commands = create_vm_commands()

    vm_image = get_vm_image_id()
    node_sku = "batch.node.ubuntu 18.04"

    task_start_commands = get_compute_start_commands(vm_image)
    task_finish_commands = get_compute_finish_commands()

    poolname = "wgs_{}{}_v3".format(reference, 'standard')

    pooldata = {
        "pool_vm_size": get_vm_size_azure(8, 64, 1),
        "cpus_per_task": 8,
        'mem_per_task': 64,
        "disk_per_task": 200,
        'dedicated': False,
        'node_resource_id': vm_image,
        'node_os_publisher': 'Canonical',
        'node_os_offer': 'UbuntuServer',
        'node_os_sku': node_sku,
        'data_disk_sizes': None,
        'max_tasks_per_node': 1,
        'auto_scale_formula': autoscale_formula,
        'create_vm_commands': vm_commands,
        'start_resources': None,
        'compute_start_commands': task_start_commands,
        'compute_finish_commands': task_finish_commands
    }

    return {poolname: pooldata}


def create_vm_commands():
    # GETSIZE AND MOUNT:
    # the disks are not guaranteed to appear under the same device name when starting a new
    # vm from a managed image. So we cannot be sure where the devices should be mounted,
    # this code uses the disk size to guess where to mount
    # If disk in under 40ish GB then mount it to refdata (our default reference disk is 32 GB)
    # If disk is over 900ish GB then mount it to datadrive (our default scratch space is 1TB)
    # DOCKER GROUP:
    # We do not have sudo available in tasks, docker requires sudo. Docker also comes with a
    # 'docker' user group. This user group has escalated permissions, any user in this group
    # can run docker without sudo (but still as an escalated user). Add the current user (default _azbatch)
    # to the docker user group. This cannot be done during the image creation, image capture removes all user
    # information.
    commands = (
        "sudo gpasswd -a $USER docker\n"
        "sudo mkdir -p /datadrive\n"
        "sudo mkdir -p /mnt/datadrive\n"
        "sudo chmod -R 777 /datadrive\n"
        "sudo chmod -R 777 /mnt/datadrive\n"
    )

    commands = literal_unicode(commands)

    return commands


def get_compute_start_commands(imageid):
    # Azure batch starts a process on each node during startup
    # this process runs the entire time VM is up (speculation?). running sudo gasswd
    # adds our user to the docker group in node startup. but all user/group
    # permission updates require restarting the bash process (normally by
    # running newgrp or by logout-login). Since we cannot do that with batch
    # and since the start task and compute task run under same process, we need
    # to explicitly specify the user group when running docker commands. sg in
    # linux can be used to set group when executing commands

    if 'docker-production-v3-standard' in imageid:
        prefix = '/mnt/datadrive'
    else:
        prefix = '/datadrive'

    commands = [
        'clean_up () {',
        '  echo "clean_up task executed"',
        '  find {}/$AZ_BATCH_TASK_WORKING_DIR/ -xtype l -delete'.format(prefix),
        '  exit 0',
        '}',
        'trap clean_up EXIT',
    ]

    commands.extend([
        'mkdir -p {}/$AZ_BATCH_TASK_WORKING_DIR/\n'.format(prefix),
        'cd {}/$AZ_BATCH_TASK_WORKING_DIR/\n'.format(prefix)
    ])

    commands = '\n'.join(commands)

    commands = literal_unicode(commands)

    return commands


def get_compute_finish_commands():
    commands = (
        'sg docker -c "docker run -v /datadrive:/datadrive -w /datadrive/$AZ_BATCH_TASK_WORKING_DIR continuumio/miniconda find . -xtype l -delete"\n',
        'sg docker -c "docker run -v /datadrive:/datadrive -w /datadrive/$AZ_BATCH_TASK_WORKING_DIR continuumio/miniconda find . -xtype f -delete"\n',
    )
    commands = ''.join(commands)

    commands = literal_unicode(commands)

    return commands


def generate_autoscale_formula(tasks_per_node, dedicated):
    if dedicated:
        node_type = "TargetDedicatedNodes"
    else:
        node_type = "TargetLowPriorityNodes"

    formula = (
        "$NodeDeallocationOption=taskcompletion;\n"
        "tasksPerNode = {0};\n"
        "numAddMax = 20;\n"
        "numDelMax = 20;\n"
        "startingNumberOfVMs = 1;\n"
        "minNumberofVMs = 0;\n"
        "maxNumberofVMs = 1000;\n"
        "pendingTaskSamplePercent = $PendingTasks.GetSamplePercent(180 * TimeInterval_Second);\n"
        "pendingTaskSamples = pendingTaskSamplePercent < 70 ? startingNumberOfVMs : avg($PendingTasks.GetSample(180 * TimeInterval_Second));\n"
        "cores = ${1} * tasksPerNode;\n"
        "$extraVMs = (pendingTaskSamples - cores) / tasksPerNode;\n"
        "$extraVMs = $extraVMs + (tasksPerNode-1)/tasksPerNode;\n"
        "$extraVMs = min(numAddMax, $extraVMs);\n"
        "$extraVMs = max(-numDelMax, $extraVMs);\n"
        "targetVMs = (${1} + $extraVMs);\n"
        "${1} = max(minNumberofVMs,min(maxNumberofVMs, targetVMs));\n"
    )

    formula = formula.format(tasks_per_node, node_type)

    formula = literal_unicode(formula)

    return formula


def get_batch_params(override=None):
    data = {
        "storage_container_name": "tasks-container",
        "no_delete_pool": True,
        "no_delete_job": False,
        "reference": "grch37"
    }

    data = override_config(data, override)

    return data


def write_config(params, filepath):
    with open(filepath, 'w') as outputfile:
        yaml.dump(params, outputfile, default_flow_style=False)


def get_batch_config(defaults, override=None):
    pools = {}
    pools.update(generate_standard_pool(defaults['reference']))
    pools.update(generate_multicore_pool(defaults['reference']))

    config = {
        'pools': pools,
        "storage_container_name": defaults["storage_container_name"],
        "no_delete_pool": defaults["no_delete_pool"],
        "no_delete_job": defaults["no_delete_job"],
        "pypeliner_storage_account": "wgspypeliner"
    }

    config = override_config(config, override)

    return config


def generate_submit_config_in_temp(args):
    azure_submit = ['azurebatch',
                    'pypeliner.contrib.azure.batchqueue.AzureJobQueue']
    if not args.get("submit", None) in azure_submit:
        return args

    if args['which'] == 'generate_config':
        return args

    batch_yaml = "batch.yaml"
    tmpdir = args.get("tmpdir", None)
    pipelinedir = args.get("pipelinedir", None)

    # use pypeliner tmpdir to store yaml
    if pipelinedir:
        batch_yaml = os.path.join(pipelinedir, batch_yaml)
    elif tmpdir:
        batch_yaml = os.path.join(tmpdir, batch_yaml)
    else:
        logging.getLogger("wgs.generate_batch_config").warn(
            "no tmpdir specified, generating configs in working dir"
        )
        batch_yaml = os.path.join(os.getcwd(), batch_yaml)

    helpers.makedirs(batch_yaml, isfile=True)

    batch_yaml = helpers.get_incrementing_filename(batch_yaml)

    params_override = args.get("config_override", {})

    config_params = get_batch_params(override=params_override)
    config = get_batch_config(config_params, override=params_override)
    write_config(config, batch_yaml)

    args["submit_config"] = batch_yaml

    return args
