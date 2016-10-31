from flask import current_app, g, jsonify
from models import Properties
from datetime import datetime
import inspect
import traceback


def debug_msg(message,keyword1=-99,keyword2=-99,keyword3=-99,keyword4=-99,keyword5=-99,keyword6=-99,keyword7=-99,keyword8=-99,keyword9=-99,keyword10=-99):
    msg = ''
    property = Properties.query.filter_by(key = 'DEBUG').first()
    if property.value != None and property.value == 'true':
        callerframerecord = inspect.stack()[1]    # 0 represents this line
                                                  # 1 represents line at caller
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        msg += str(datetime.today())
        msg += '\t' + 'MSG:' + str(message)
        try:
            msg += '\t' + 'USER:' + str(g.user.username)
        except:
            msg += '\t' + 'USER:' + str("BackendUser")
        msg += '\t' + 'FILE:' + str(info.filename)
        msg += '\t' + 'FUNC:' + str(info.function)
        msg += '\t' + 'LINE:' + str(info.lineno)
#         msg += '\t' + 'CALL:' + str(traceback.format_stack(limit=5))
        
        msg += '\t'
        if(keyword1!=-99):
            msg += 'KEY1:' + str(keyword1)
        msg += '\t'
        if(keyword2!=-99):
            msg += 'KEY2:' + str(keyword2)
        msg += '\t'
        if(keyword3!=-99):
            msg += 'KEY3:' + str(keyword3)
        msg += '\t'        
        if(keyword4!=-99):
            msg += 'KEY4:' + str(keyword4)
        msg += '\t'
        if(keyword5!=-99):
            msg += 'KEY5:' + str(keyword5)
        msg += '\t'
        if(keyword6!=-99):
            msg += 'KEY6:' + str(keyword6)
        msg += '\t'
        if(keyword7!=-99):
            msg += 'KEY7:' + str(keyword7)
        msg += '\t'
        if(keyword8!=-99):
            msg += 'KEY8:' + str(keyword8)
        msg += '\t'
        if(keyword9!=-99):
            msg += 'KEY9:' + str(keyword9)
        msg += '\t'
        if(keyword10!=-99):
            msg += 'KEY10:' + str(keyword10)
# Open log file in append mode
        f = open(current_app.config['LOG_FILE'],'a')
#        f.write(str(datetime.today()))
        f.write(msg)
        print msg
        f.write('\n')
        f.close()