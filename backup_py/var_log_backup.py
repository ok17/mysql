# coding: utf-8

"""var log backup to s3bucket.

Usage:
    var_log_s3backup.py [--date=<date>]
    var_log_s3backup.py -h | --help
    var_log_s3backup.py -v | --version

Options:
    --date=<date>   Set covered date.format=%Y%m%d
    -h --help       Show this screen.
    -v --version    Show version.

"""

import datetime
import dircache
import json
import re
import shlex
import smtplib
import sys
from email.MIMEText import MIMEText
from email.Utils import formatdate
from subprocess import Popen, PIPE
from docopt import docopt
from schema import Schema, SchemaError, And, Or, Use


def create_message(from_address, to_address, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Date'] = formatdate()
    return msg


def validate_args(args):
    schema = Schema({
        '--date': Or(None, lambda n: re.match('\d{8}', n) is not None, error='--date should be date_format=yyyymmdd'),
        '--help': bool,
        '--version': bool,
    })

    return schema.validate(args)


def main():
    sys.stdout.write('%s\t%s start\n' % (str(datetime.datetime.now()), __file__))

    args = docopt(__doc__, version='{0} {1}'.format(__file__, '1.0'))
    try:
        args = validate_args(args)

        if args['--date'] is None:
            covered_date = datetime.datetime.now().strftime('%Y%m%d')
            year = datetime.datetime.now().strftime('%Y')
            month = datetime.datetime.now().strftime('%m')
        else:
            covered_date = args['--date']
            year = covered_date[0:4]
            month = covered_date[4:6]

    except SchemaError as e:
        print(e)
        sys.exit(1)

    hostname = Popen(['sh', 'hostname.sh'], stdout=PIPE).communicate()[0].rstrip()

    f = open('config.json', 'r')
    json_data = json.load(f)

    from_address = '%s@%s' % (hostname, json_data['domain'])
    to_address = json_data['sendmail']

    s3bucket = json_data['s3bucket']
    target_list = json_data['target']

    batch_list = {}
    for target in target_list:
        batch_list[target] = target_list[target]
    f.close()

    count = 0
    output = []
    for batch in batch_list:
        output.append('%s\n' % batch)

        s3path = '%slog/%s/%s/%s/%s/' % (s3bucket, batch, hostname, year, month)
        file_name_list = dircache.listdir(batch_list[batch])
        for file_name in file_name_list:
            if file_name.find(covered_date) != -1:
                cmdline = 's3cmd put --rr %s%s %s' % (batch_list[batch], file_name, s3path)
                args = shlex.split(cmdline.encode('euc-jp'))
                s3 = Popen(args, stdout=PIPE)
                output.append(s3.communicate()[0])

                count += 1

        output.append('\n')

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