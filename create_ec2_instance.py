#!/usr/bin/python3

import utils

def main():
    args = utils.parser_create_ec2_instance()
    utils_utils = utils.Utils()
    utils_utils.create_ec2_instance(region=args.region,architecture=args.architecture,instance_name=args.instance_name,disk_size=args.disk_size)

if __name__ == "__main__":
    main()
    