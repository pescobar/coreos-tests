#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import json
from jinja2 import Template

def main():

    args = parse_input()

    # read config file
    json_cfg_file = os.path.abspath(args.cfgfile.name)
    json_data = open(json_cfg_file)
    cfg = json.load(json_data)

    app_name = cfg['app_name']
    service_name = cfg['services'][0]['service_name']
    domains = cfg['services'][0]['components'][0]['domains']

    components = []
    for component in cfg['services'][0]['components']:
        components.append(component)
        #print component

    if args.action == 'start':

        components_to_launch = []
        for component in components:

            # do the replacement in the template
            template = Template(get_jinja2_template())
            component['environment'] = args.environment
            if 'dependencies' in component.keys():
                component['dependency_name'] = component['dependencies'][0]['name']
                component['dependency_service_name'] = service_name + '-' + component['dependencies'][0]['name']
                #print component['dependency_service_name']
            final_template = template.render(component)

            # write the unit file to disk
            # the unit file contains the service name defined in config file
            # I use the service name to "group" containers in pods
            service_filename = '/tmp/{0}-{1}.service'.format(service_name, component['component_name'])
            text_file = open(service_filename, "w")
            text_file.write(final_template)
            text_file.close()

            # save path to template files in components_to_launch[]
            # if the component has dependencies append it. If it has no dependencies insert it at beggining
            if 'dependencies' in component.keys():
               components_to_launch.append(service_filename)
            else:
                components_to_launch.insert(0, service_filename)

        #print components_to_launch

        for unit_file in components_to_launch:

            # launch the unit file
            cmd = 'fleetctl start {0}'.format(unit_file)
            stdout, stderr, retcode = run_cmd(cmd)
            if retcode == 0:
                print stdout
            else:
                print "something went wrong man!"

        #for unit_file in components_to_launch:
            #os.remove(service_filename)

    if args.action == 'status':
        cmd = 'fleetctl list-units | grep {0}'.format(app_name)
        stdout, stderr, retcode = run_cmd(cmd)
        if retcode == 1:
            print 'container not running'
        else:
            print stdout

    if args.action == 'stop':
        for component in components:
            cmd = 'fleetctl unload {0}-{1}.service'.format(service_name, component['component_name'])
            stdout, stderr, retcode = run_cmd(cmd)

def parse_input():
    parser = argparse.ArgumentParser(description='create and submit unit files to the coreOS cluster')
    parser.add_argument('--action', '-a', choices=['start', 'stop', 'status'], default='status', help='choose the desired action')
    parser.add_argument('--cfgfile', '-c', type=argparse.FileType('r'), help='config file', required = True)
    parser.add_argument('--environment', '-e', choices=['prod', 'dev'], default='prod', help='choose the environment to use')
    return parser.parse_args()

def get_jinja2_template():
    return """[Unit]
Description={{ component_name }}
Requires=docker.service
After=docker.service

[Service]
TimeoutStartSec=0
Restart=on-failure

ExecStartPre=-/usr/bin/docker kill {{ component_name }}
ExecStartPre=-/usr/bin/docker rm {{ component_name }}
ExecStartPre=/usr/bin/docker pull {{ image }}

{% if dependency_name is defined %}
ExecStart=/usr/bin/docker run --link {{ dependency_name }}:{{ dependency_name }} --name {{ component_name }} -p {{ ports }}:{{ ports }} {{ image }}
{% else %}
ExecStart=/usr/bin/docker run --name {{ component_name }} -p {{ ports }}:{{ ports }} {{ image }}
{% endif %}

ExecStartPost=/usr/bin/etcdctl set /domains/%H/{{ domains }}:{{ external_port }} running
ExecStop=/usr/bin/docker stop {{ component_name }}
ExecStopPost=/usr/bin/etcdctl rm /domains/%H/{{ domains }}:{{ external_port }}

[X-Fleet]
MachineMetadata=env={{ environment }}
{% if dependency_service_name is defined %}
MachineOf={{ dependency_service_name }}.service
{% endif %}

"""

def run_cmd(cmd):
    """ returns stdout, stderr and exit code """
    try:
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        stdout, stderr = ps.communicate()
    except subprocess.CalledProcessError as e:
        print e.output
    return stdout, stderr, ps.returncode

if __name__ == "__main__":
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
