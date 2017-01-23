'''Program for converting windows phone vmsg files to android xml files.'''
## Type 1 is other person, type two is self.
## SENDBOX is self, INBOX is other person.
## SENDBOX==2, INBOX==1
import time
import calendar
import copy

def parse_vals(tmp_holder, line):
    '''Checks the line to see if we can retrieve data from it.'''
    line = line.split(':', 1)
    if line[0] == 'TEL':
        tmp_holder['address'] = line[1]
    elif line[0] == 'X-BOX':
        if line[1] == 'INBOX':
            tmp_holder['type'] = '1'
        else:
            tmp_holder['type'] = '2'
    elif line[0] == 'X-READ':
        if line[1] == 'READ':
            tmp_holder['read'] = '1'
        else:
            tmp_holder['read'] = '0'
##    elif line[0] == 'X-SIMID':
##        pass ## Do nothing
    elif line[0] == 'X-LOCKED':
        if line[1] == 'UNLOCKED':
            tmp_holder['locked'] = '0'
        else:
            tmp_holder['locked'] = '1'
##  elif line[0] == 'X-TYPE':
##        pass ## Do nothing
    elif line[0] == 'Date':
        tmp_time = time.strptime(line[1], '%Y/%m/%d %H:%M:%S')
        tmp_holder['date'] = str(calendar.timegm(tmp_time))
        tmp_time = time.localtime(calendar.timegm(tmp_time))
        tmp_holder['readable_date'] = time.strftime('%b %d, %Y %H:%M:%S %p',
                                                    tmp_time)
    elif line[0][:8] == 'Subject;':
        tmp_holder['body'] = line[1]

def parse_vmsg():
    '''Reads lines from sms.vmsg for conversion.'''
    f_name = 'sms.vmsg'

    msgs = []
    tmp_holder = {
        'address':None,
        'type':None,
        'read':None,
        'locked':None,
        'date':None,
        'readable_date':None,
        'body':None,

        'protocol':'0',
        'subject':'null',
        'toa':'null',
        'sc_toa':'null',
        'service_center':'null',
        'status':'-1',
        'date_sent':'0'
        }

    in_msg = False
    try:
        with open(f_name, 'r') as temp_f:
            ##print('test')
            for line in temp_f.readlines():
                line = line.strip()
                ##print(line)
                if not in_msg and line == 'BEGIN:VMSG': ## Not currently in message.
                    in_msg = True
                elif line == 'END:VMSG':
                    ## Have it put the message on the list.
                    msgs.append(copy.deepcopy(tmp_holder))
                    in_msg = False
                else:
                    parse_vals(tmp_holder, line)
        return msgs, None
    except IOError:
        print('Error, make sure your vmsg file is named sms.vmsg and is in the same folder.')
    return None, 1

def convert():
    '''Base function for conversion that calls parse_vmsg and writes to sms.xml.'''
    msgs, err = parse_vmsg()
    if err != None:
        return

    o_file_name = 'sms.xml'
    hder = """ <?xml version='1.0' encoding='UTF-8' standalone='yes' ?>\n """
    hder += """ <!--File Created By vmsg2xml-->\n """
    hder += """ <?xml-stylesheet type="text/xsl" href="sms.xsl"?>\n<smses count=" """
    hder += str(len(msgs))
    hder += """" backup_date="none">\n"""

    with open(o_file_name, 'a') as temp_f:
        temp_f.write(hder)
        for item in msgs:
            app_line = '  <sms protocol="0" address="'\
                + item['address'] + '" date="' + item['date']\
                + '" type="1" subject="null" body="'\
                + item['body']\
                + '" toa="null" sc_toa="null" service_center="null" read="1" status="-1"'\
                + ' locked="0" date_sent="'\
                + item['date_sent']\
                + '" readable_date="'\
                + item['readable_date'] + '" />\n'
            temp_f.write(app_line)
        temp_f.write('</smses>')

if __name__ == '__main__':
    print('Starting converstion.')
    convert()
    print('Conversion complete!')
    print('Your messages should be in a file called sms.xml.')
