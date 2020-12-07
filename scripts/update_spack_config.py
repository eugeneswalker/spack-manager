#!/usr/bin/env spack-python
import spack.config
import spack.util.spack_yaml as syaml
import sys
import llnl.util.tty as tty
import shutil
import os

def update(config, cfg_file):
    """
    Courtesy of Greg Becker
    """
    # Get a function to update the format
    update_fn = spack.config.ensure_latest_format_fn(config)
    with open(cfg_file) as f:
        raw_data = syaml.load_config(f) or {}
        data = raw_data.pop(config, {})
    update_fn(data)
    # Make a backup copy and rewrite the file
    bkp_file = cfg_file + '.bkp'
    shutil.copy(cfg_file, bkp_file)
    write_data = config
    with open(cfg_file, 'w') as f:
        syaml.dump_config(write_data, stream=f, default_flow_style=False)
    msg = 'File "{0}" updated [backup={1}]'
    tty.msg(msg.format(cfg_file, bkp_file))

if __name__ == '__main__':
    updateDir = sys.argv[1]
    cfgs = ['config', 'packages', 'compilers']
    for c in cfgs:
        fle = os.path.join(updateDir, '%s.yaml' % c)
        if os.path.isfile(fle):
            update(c, fle)
