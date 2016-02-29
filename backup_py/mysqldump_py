# coding: utf-8

import datetime
import json
import os
import shlex
import smtplib
import sys
import MySQLdb
from email.MIMEText import MIMEText
from email.Utils import formatdate
from subprocess import Popen, PIPE


def create_message(from_address, to_address, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Date'] = formatdate()
    return msg


def main():
    sys.stdout.write('%s\t%s start\n' % (str(datetime.datetime.now()), __file__))

    hostname = Popen(['sh', 'hostname.sh'], stdout=PIPE).communicate()[0].rstrip()
    year = datetime.datetime.now().strftime('%Y')
    month = datetime.datetime.now().strftime('%m')

    f = open('config.json', 'r')
    json_data = json.load(f)

    from_address = hostname + '@' + json_data['domain']
    to_address = json_data['sendmail']

    s3bucket = json_data['s3bucket']
    dbhost = json_data['mysqlhost']
    dbuser = json_data['mysqluser']
    dbpass = json_data['mysqlpass']

    f.close()

    connect = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, charset='utf8')
    cursor = connect.cursor()
    cursor.execute('SHOW DATABASES')
    databases = cursor.fetchall()
    cursor.close()
    connect.close()

    count = 0
    output = []
    execute_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    ignore_database = ['information_schema', 'mysql', 'performance_schema']
    for database in databases:
        if database[0] not in ignore_database:
            dump_file = '%s.dump-%s' % (database[0], execute_time)
            dump_path = '/tmp/%s' % dump_file

            dump_cmd = 'mysqldump -h%s -u %s -p%s --opt %s --result-file=%s' % (dbhost, dbuser, dbpass, database[0], dump_path)
            dump_args = shlex.split(dump_cmd.encode('euc-jp'))
            dump = Popen(dump_args, stdout=PIPE)
            output.append(dump.communicate()[0])

            gz_cmd = 'gzip %s' % dump_path
            gz_args = shlex.split(gz_cmd.encode('euc-jp'))
            gz = Popen(gz_args, stdout=PIPE)
            output.append(gz.communicate()[0])

            s3path = '%sdump/%s/%s/%s/%s.gz' % (s3bucket, hostname, year, month, dump_file)
            s3_cmd = 's3cmd put --rr %s.gz %s' % (dump_path, s3path)
            args = shlex.split(s3_cmd.encode('euc-jp'))
            s3 = Popen(args, stdout=PIPE)
            output.append(s3.communicate()[0])

            os.remove('%s.gz' % dump_path)

            count += 1

    result = ''.join(output)

    if count == 0:
        subject = '[warning] %s' % __file__
    else:
        subject = '[success] %s' % __file__

    msg = create_message(from_address, to_address, subject, result)
    server = smtplib.SMTP('localhost')
    server.sendmail(from_address, to_address, msg.as_string())
    server.quit()

    sys.stdout.write('%s\t%s end\n' % (str(datetime.datetime.now()), __file__))

if __name__ == '__main__':
    main()