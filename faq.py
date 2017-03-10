import yaml
import configparser
import sys
import shutil

config = configparser.ConfigParser()
if len(sys.argv)<2:
    config.read('litm.cfg')
else:
    config.read(sys.argv[1])

faq_dest = config.get('path','faq_dest')
faq_dir = config.get('path','faq_dir')

y=yaml.load(open(faq_dir+'/faq.yaml'))
tags=set()
for yy in y:
    tags.update(yy['tags'])

with open(faq_dest+'/tags.yaml', 'w') as f:
    f.write(yaml.dump(sorted(list(tags)),default_flow_style=False))

#need to copy faq.yaml to compiled directory
shutil.copyfile(faq_dir + '/faq.yaml', faq_dest +'/faq.yaml')
