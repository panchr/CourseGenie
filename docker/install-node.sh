# docker/install-node.sh
# Author: Rushy Panchal
# Date: April 4th, 2017
# Description: Install NodeJS through nvm.

sudo apt-get install -y curl
PROFILE=~/.profile curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.32.1/install.sh | bash

source ~/.profile
nvm install "$NODE_VERSION"
nvm alias default "$NODE_VERSION"

npm install -g gulp-cli
