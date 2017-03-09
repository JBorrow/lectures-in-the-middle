import yaml
import configparser
import sys
import shutil

config = configparser.ConfigParser()
if len(sys.argv)<2:
    config.read('litm.cfg')
else:
    config.read(sys.argv[1])

compile_dir = config.get('path','compile_dir')
faq_dir = config.get('path','faq_dir')

y=yaml.load(open(faq_dir+'/faq.yaml'))
tags=set()
for yy in y:
    tags.update(yy['tags'])

with open(compile_dir+'/tags.yaml', 'w') as f:
    f.write(yaml.dump(list(tags),default_flow_style=False))

#need to copy faq.yaml to compiled directory
shutil.copyfile(faq_dir + '/faq.yaml', compile_dir +'/faq.yaml')
