import ply.lex as lex
import ply.yacc as yacc
import sys
import os
import shutil
import random
import re
import tempfile
import subprocess
import tidylib as tidy
import ltmd
import yaml
import pypandoc

import configparser

config = configparser.ConfigParser()
if len(sys.argv)<2:
    config.read('litm.cfg')
else:
    config.read(sys.argv[1])
compile_dir = config.get('path','compile_dir')
tex_dir = config.get('path','tex_dir')
image_dir = config.get('path','image_dir')
web_dir = config.get('path','web_dir')
args = sys.argv
own_files = [ f.strip() for f in config.get('path','own_files').split(',')]

def getUID():
    return "{:0<10}".format(random.randint(0, 1e10))

def register(key,value,uid):
    for k,dic in [('keypoint',lexer.keypoints),('image',lexer.images),('question',lexer.questions)]:        
        if key==k:
            if not lexer.current['section'] in dic.keys():
                dic[lexer.current['section']]=[]
            if not lexer.current['lecture'] in dic.keys():
                dic[lexer.current['lecture']]=[]
            dic[lexer.current['section']].append(value)
            dic[lexer.current['lecture']].append(value)
    if key in ['section','lecture']:
        lexer.begin[key][value]=uid
        lexer.end[key][lexer.current[key]]=uid
        lexer.current[key]=value
    if key=='section':
        lexer.sections.append(value)
    if key=='lecture':
        lexer.lectures.append(value)
    lexer.uids[key][value]=uid

tokens=(
    'KEY',
    'TEXT',
    'PDFONLYBEGIN',
    'PDFONLYEND',
)


def t_KEY(t):
    r'%%\\(?P<key>\w+)\{(?P<value>.*)\}'
    key=lexer.lexmatch.group('key')
    value=lexer.lexmatch.group('value')
    uid=getUID()
    register(key,value,uid)
    t.value=(key,value,uid)
    return t

def t_PDFONLYBEGIN(t):
    r'%%@pdfonly(?P<txt>.*?)'
    t.value=('PDFONLYBEGIN',lexer.lexmatch.group('txt'))
    return t

def t_PDFONLYEND(t):
    r'%%@endpdfonly'
    t.value=('PDFONLYEND',lexer.lexmatch.group('txt'))
    return t

def t_TEXT(t):
    r'(?:(?:\\%)|(?:[^%\\]+)|(?:\\[^%])|(%[^%])|(?:%%[^\\@]))+'
    t.value=('TEXT',t.value)

    return t

def p_blocks(p):
    'blocks : block blocks'
    #if the block is ignored the result is None
    if p[1]:
        p[0] = [p[1]]+p[2]
    else:
        p[0]=p[2]

def p_blocksnone(p):
    'blocks : '
    p[0] = []

def p_pdfonly(p):
    'PDFONLY : PDFONLYBEGIN blocks PDFONLYEND'
    p[0] = ('PDFONLY',p[2])    
    
def p_block(p):
    '''block : TEXT
             | KEY
             | PDFONLY
'''
    p[0] = p[1]

def insertLectureDivs(origTxt):
    txt=str(origTxt)
    for i,uid in lexer.uids['lecture'].items():
        comment=r"<!-- {} -->".format(uid)
        div='''
<div id="lecture-{i}" class="lecture">
  <hr>Lecture {i}
</div>
        '''.format(i=i)
        txt=txt.replace(comment,div)
    return txt

def format_classes(classes):
    return ' '.join(classes)

def getKeyPointsHTML(key, extra_class=[]):
    classes = format_classes(extra_class + ['keypoints'])
    if key not in lexer.keypoints.keys():
        return ''
    else:
        txt='<div class="{}">\n<h2>\nKey Points\n</h2>'.format(classes)
        for kp in lexer.keypoints[key]:
            div='''<div class="key-point">{kptxt}</div>'''.format(
                kptxt=pypandoc.convert(kp,'html',format='tex'))
            txt+=div
        txt+='</div>'
        return txt

def getQuestionsHTML(key, extra_class=[]):
    classes = format_classes(extra_class + ['questions'])
    if key not in lexer.questions.keys():
        return ''
    else:
        txt='<div class="{}">\n<h2>\nQuick Questions\n</h2>'.format(classes)
        for kp in lexer.questions[key]:
            div='''<div class="question">{kptxt}</div>'''.format(
                kptxt=pypandoc.convert(kp,'html',format='tex'))
            txt+=div
        txt+='</div>'
        return txt

def run_pandoc(content, bibliography=""):
    if bibliography:
        bib = ["--bibliography={}".format(bibliography)]
    else:
        bib = []

    extra_args = [
        "--mathjax",
        "-F",
        "pandoc-crossref",
        "-F",
        "pandoc-citeproc"] + bib

    print("Running Pandoc (MD -> HTML)")
    OutputData = pypandoc.convert_text(content, "html", format="md", extra_args=extra_args)

    return OutputData

lexer=lex.lex()
lastLecture=0

def process(fileName):
    global lastLecture
    # prepare lexer state

    lexer.current={'section':'begining','lecture':'begining'}
    lexer.keypoints={}
    lexer.questions={}
    lexer.images={}
    lexer.uids={ 'section':{}, 'lecture':{} , 'keypoint':{}, 'image':{}, 'question':{}}
    lexer.begin={'section':{}, 'lecture':{}}
    lexer.end={'section':{}, 'lecture':{} }
    lexer.sections=[]
    lexer.lectures=[]
    # parse the tex file

    f=open(tex_dir + fileName,'r')
    txt=f.read()
    lexer.input(txt)
    parser = yacc.yacc()
    result = parser.parse(txt)

    # prepare tex file for conversion to MD
    
    fullTxt=""
    for token in result:
        if token[0]=="TEXT":
            fullTxt+=token[1]
        elif token[0]=='PDFONLY':
            pass   #this is ignored here 
        else:
            fullTxt+="\nMDCOMMENT"+token[2]+"\n"

    # use ltmd to convert
    
    InputText=fullTxt

    # Before we do, remove any random \rules, and \ces

    InputText = re.sub(r"\\rule{.*?}{.*?}",
                        "",
                        InputText)
    #InputText = InputText.replace("\ce", "")

    PreProcessed = ltmd.PreProcess(InputText, ImgPrepend="/")
    Pandocced = ltmd.RunPandoc(PreProcessed.ParsedText, extra=["--mathjax"])
    PostProcessed = ltmd.PostProcess(Pandocced, PreProcessed.ParsedData)
    OutputText = PostProcessed.ParsedText

    # add a last line marker to terminate the opened sections and lectures
    
    fullMD=OutputText.replace('MDCOMMENT',r'[\\] # ')
    endUID=getUID()
    fullMD+=r"[\\] # "+endUID+"\n"
    lexer.end['section'][lexer.current['section']]=endUID
    lexer.end['lecture'][lexer.current['lecture']]=endUID

    # MD --> HTML conversion
    
    fullMDforHTML=re.sub(r"\[\\\\\] # (\d+)", r"<!-- \1 -->", fullMD)
    html=run_pandoc(fullMDforHTML, bibliography=tex_dir + 'bibliography.bib')

    # separate the sections 

    db={'sections':{}}
    seclist=[]
    for sec in lexer.sections:
        regex= r'<!-- {} -->'.format(lexer.begin['section'][sec])
        regex+='(?P<txt>.*?)'
        regex+=r'<!-- {} -->'.format(lexer.end['section'][sec])

        match=re.search(regex ,html,re.MULTILINE+re.DOTALL)
        txt=match.group('txt')
        txt=insertLectureDivs(txt)
        txt+=getKeyPointsHTML(sec)
        txt+=getQuestionsHTML(sec)
        with open(compile_dir + '_'+sec.replace(' ','_')+'.html','w') as of:
            tidy_options = {
                "doctype" : "omit",
                "show-body-only": "yes",           
            }        
            th,errs=tidy.tidy_document(txt, tidy_options)
            of.write(th)
        lecs={}
        if sec in lexer.keypoints.keys():
            for kp in lexer.keypoints[sec]:
                for lec in lexer.keypoints.keys():
                    if lec!=sec :
                        if kp in lexer.keypoints[lec]:
                            if not lec in lecs.keys():
                                lecs[lec]=[]
                            lecs[lec].append(kp)
        if sec in lexer.images.keys():
            images=lexer.images[sec]
        else:
            images=None

        lecnbrs=sorted([int(k) for k in lecs.keys() if not k=='begining' ])
        if lecnbrs:
            lastLecture=lecnbrs[-1]
        leclist=[ {'number':str(i),'kps':lecs[str(i)]} for i in lecnbrs ]
        # treat the case of split lecture
        if 'begining' in lecs.keys():    
            leclist.insert(0,{'number':str(lastLecture),'kps':lecs['begining']})
        if images:
            seclist.append({'lectures':leclist,'name':sec,'image':images[0]})
        else:
            seclist.append({'lectures':leclist,'name':sec})

        if sec in lexer.keypoints.keys():
            items=['\\item {0}'.format(kp) for kp in lexer.keypoints[sec]]
            with open(compile_dir+"/{0}_keypoints.tex".format(sec.replace(' ','-')),'w') as kptex:
                kptex.write("\n".join(items))


            
    leclist=[]
    for lec in lexer.lectures:
        firstSplit,lastSplit=False,False
        if lec==lexer.lectures[0] and lec not in lexer.begin['lecture'].keys():
            # use the first section as the begining of the lecture
            firstSplit=True
            labelBegin=lexer.begin['section'][lexer.sections[0]]
        else:
            labelBegin=lexer.begin['lecture'][lec]
        if lec==lexer.lectures[-1] and lec not in lexer.end['lecture'].keys():
            # use the first section as the begining of the lecture
            lastSplit=True
            labelEnd=lexer.end['section'][lexer.sections[-1]]
        else:
            labelEnd=lexer.end['lecture'][lec]
        regex= r'<!-- {} -->'.format(labelBegin)
        regex+='(?P<txt>.*?)'
        regex+=r'<!-- {} -->'.format(labelEnd)

        match=re.search(regex ,html,re.MULTILINE+re.DOTALL)
        
        txt=getKeyPointsHTML(lec, extra_class=['lecture-kps'])
        txt+=match.group('txt')
        txt+=getQuestionsHTML(lec, extra_class=['lecture-qs'])
        if firstSplit:
            rwaccess='a'
        else:
            rwaccess='w'
        with open(compile_dir + '_Lecture_'+lec+'.html',rwaccess) as of:
            tidy_options = {
                "doctype" : "omit",
                "show-body-only": "yes",           
            }        
            th,errs=tidy.tidy_document(txt, tidy_options)
            of.write(th)

        if lec in lexer.images.keys():
            images=lexer.images[lec]
        else:
            images=None
        
        
        if images:
            leclist.append({'name':lec,'image':images[0]})
        else:
            leclist.append({'name':lec})


            
    return seclist,leclist


def get_tex(directory):
    if not own_files:
        raw = os.listdir(directory)
        files = []
        for filename in raw:
            if filename[-3:] == 'tex':
                files.append(filename)
            else:
                pass

        return files
    
    return own_files

dbSections=[]
dbLectures=[]

try:
    os.mkdir(compile_dir)
except OSError:
    pass

files = get_tex('./tex')

for f in files:
    print("Compiling {}".format(f))
    seclist,leclist=process(f)
    dbSections.append({'name':f.split('.')[0],'sections':seclist})
    dbLectures.extend(leclist)

with open('./compiled/information.yaml', 'w') as f:
    f.write(yaml.dump(dbSections))
with open('./compiled/lectures.yaml', 'w') as f:
    f.write(yaml.dump(dbLectures))

### Now we must deal with files, building middleman etc.

op_img_dir = web_dir + 'source/images/'
op_data_dir = web_dir + 'data/'
op_notes_dir = web_dir + 'source/notes/'
op_lectures_dir = web_dir + 'source/lectures/'

for dir in [op_img_dir, op_data_dir, op_notes_dir, op_lectures_dir]:
    try:
        os.mkdir(dir)
    except OSError:
        pass

print("Copying Images...")
for img in os.listdir(image_dir):
    shutil.copyfile(image_dir + img, op_img_dir + img)

print("Copying Compiled Files...")

dispatch=[]
for ftype in config.options('files'):
    dispatch.append(
        (re.compile(config.get('files',ftype)), config.get('destination',ftype) )
    )


for compiled in os.listdir(compile_dir):
    found=False
    for regex,dest in dispatch:
        if regex.match(compiled):
            found=True
            print("sending {} to {}".format( compiled,dest ))
            shutil.copyfile(compile_dir +'/'+  compiled, dest +'/' + compiled)
            break
    if not found:
        print("Unable to classify file {}{}".format(compile_dir, compiled))
        
### Middleman stuff

os.chdir(web_dir)

try:
    print("Removing old build files")
    shutil.rmtree("./build/")
except FileNotFoundError:
    # no old build files
    pass

print("Building new middleman files")
os.system("bundle exec middleman build")
