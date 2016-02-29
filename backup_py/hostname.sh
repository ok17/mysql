!/bin/bash

export AWS_ACCESS_KEY='xxxxxxxxxx'
export AWS_SECRET_KEY='xxxxxxxxxx'
export EC2_HOME='/opt/aws/apitools/ec2'
export JAVA_HOME='/usr/lib/jvm/jre'

INSTANCE=`curl -s http://169.254.169.254/latest/meta-data/instance-id`
REGION=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed -e 's/.$//g'`
TAG_NAME=`/opt/aws/bin/ec2-describe-instances --region ${REGION} ${INSTANCE} | grep ^TAG | grep Name | cut -f 5`

echo ${TAG_NAME}