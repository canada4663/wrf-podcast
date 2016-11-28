sudo yum update
sudo yum install git setuptools python-devel libxml2-devel libxml2 libxslt-devel libxslt
git clone https://github.com/canada4663/wrf-podcast.git
pip install virtualenv
cd wrf-podcast
virtualenv .
source bin/activate
pip install -r requirements.txt
sh refreshDeployment.sh
