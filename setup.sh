sudo yum update
sudo yum install git python-devel libxml2-devel libxml2 libxslt-devel libxslt
sudo pip install setuptools virtualenv
git clone https://github.com/canada4663/wrf-podcast.git
cd wrf-podcast
virtualenv .
source bin/activate
pip install --upgrade pip
pip install -r requirements.txt
sh refreshDeployment.sh
