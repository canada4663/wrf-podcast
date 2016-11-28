#sudo yum update
#sudo yum install git setuptools python-devel libxml2-devel libxml2 libxslt-devel libxslt
#git clone https://github.com/canada4663/wrf-podcast.git
#pip install virtualenv
#cd wrf-podcast
#virtualenv .
#source bin/activate
#pip install -r requirements.txt
cd lib/python2.7/site-packages/ && zip -r9 ../../../wrfpodcast.zip * && cd ../../..
cd lib64/python2.7/site-packages/ && zip -r9 ../../../wrfpodcast.zip * && cd ../../..
zip -r9 wrfpodcast.zip wrfpodcast.py
aws lambda update-function-code --function-name wrf-podcast --zip-file fileb://wrfpodcast.zip --region us-west-2
