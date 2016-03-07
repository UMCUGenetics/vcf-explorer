# vcf-explorer

# Setup MongoDB
See mongodb docs for installation instructions: http://docs.mongodb.org/manual/installation/

## mongodb.conf
```
fork = false
bind_ip = 127.0.0.1
port = 27017
quiet = true
dbpath = /path/to/db
storageEngine = wiredTiger
logpath = /path/to/mongod.log
logappend = true
journal = true
```
## Start mongodb
```
mongod -f mongodb.conf
```

# Setup vcf-explorer
## Install
```bash
git clone git@github.com:CuppenResearch/vcf-explorer.git
cd vcf-explorer
virtualenv env
. env/bin/activate

pip install -r requirements.txt
```

# Resetdb and create indexes
```
python vcfexplorer.py resetdb
```

# Upload a vcf file
```
python vcfexplorer.py vcf gatk|delly path/to/file.vcf
```

# Run flask development server
```
python vcfexplorer.py runserver -p PORT -host HOSTNAME
```
