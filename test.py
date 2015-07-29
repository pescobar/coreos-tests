#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import ConfigParser
import os
from string import Template

def main():

    # read config file and fetch a template of the unit file
    args = parse_input()
    Config = ConfigParser.ConfigParser()
    Config.read(os.path.abspath(args.infile.name))
    template = get_unit_file_template()

    # fetch global settings from config file
    name = Config.get('Global', 'name')
    env = Config.get('Global', 'env')

    # fetch info for container1 from the config file
    c1 = {}
    c1['description'], c1['name'], c1['image'], c1['domain'], c1['port'] = parse_container_config(Config, 'Container1')

    # do the replacement in the template
    src = Template(template)
    final_template = src.substitute(c1)

    # write the unit file to disk
    service_filename = '/tmp/{0}.service'.format(name)
    text_file = open(service_filename, "w")
    text_file.write(final_template)
    text_file.close()

    # launch the unit file
    cmd = 'fleetctl start {0}'.format(service_filename)
    os.system(cmd)

    # delete temp unit file
    os.system('rm -fr {0}'.format(service_filename))

def parse_input():
    parser = argparse.ArgumentParser(description='create and submit unit files to the coreOS cluster')
    parser.add_argument('infile', type=argparse.FileType('r'), help='config file')
    return parser.parse_args()

def get_unit_file_template():
    return """[Unit]
Description=$description
Requires=docker.service
After=docker.service

[Service]
TimeoutStartSec=0
Restart=on-failure

ExecStartPre=-/usr/bin/docker kill $name
ExecStartPre=-/usr/bin/docker rm $name
ExecStartPre=/usr/bin/docker pull $image

ExecStart=/usr/bin/docker run --name $name -p $port:8080 $image
ExecStartPost=/usr/bin/etcdctl set /domains/$domain/%H:$port running
ExecStop=/usr/bin/docker stop $name
ExecStopPost=/usr/bin/etcdctl rm /domains/$name/%H:%i
"""

def parse_container_config(Config, section):
    if Config.has_section(section):
        desc = Config.get(section, 'description')
        name = Config.get(section, 'name')
        image = Config.get(section, 'image')
        domain = Config.get(section, 'domain')
        port = Config.get(section, 'port')
        return desc, name, image, domain, port

if __name__ == "__main__":
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
