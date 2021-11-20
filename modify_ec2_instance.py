#!/usr/bin/python3

import utils

def main():
    args = utils.parser_modifyterminate_ec2_instance()
    utils_utils = utils.Utils()
    utils_utils.modify_ec2_instance(region=args.region,instance_id=args.instance_id)

if __name__ == "__main__":
    main()
    