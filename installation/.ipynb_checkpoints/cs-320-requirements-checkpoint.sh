#!/bin/bash

# Define colors
GREEN='\033[38;2;0;150;0m'  
LIGHTGREEN='\033[38;2;0;220;0m'  
CYAN='\033[0;36m'
NC='\033[0m'            

# Run a command and capture output
run_command() {
  "$@"
  printf "${GREEN}Done.${NC}\n\n"
}

# Update Environment
printf "${GREEN}Updating environment...${NC}\n"
run_command sudo apt-get -y update

# Upgrading system
printf "${GREEN}Upgrading system...${NC}\n"
run_command sudo apt-get -y upgrade

# Perform dist-upgrade
printf "${GREEN}Performing dist-upgrade...${NC}\n"
run_command sudo apt-get -y dist-upgrade

# Removing unnecessary packages
printf "${GREEN}Removing unnecessary packages...${NC}\n"
run_command sudo apt-get -y autoremove

# Install Python and Pip
printf "${GREEN}Installing Python & Pip...${NC}\n"
run_command sudo apt-get install -y python3-pip

# Install other apt packages
printf "${GREEN}Installing necessary apt packages...${NC}\n"
run_command sudo apt-get -y install zip unzip git graphviz

# Install Python packages
printf "${GREEN}Installing general Python packages...${NC}\n"
run_command pip3 install jupyter pandas numpy matplotlib requests statistics graphviz ipython

# MP4
printf "${GREEN}Installing packages for MP4...${NC}\n"
run_command pip3 install selenium Flask lxml html5lib

# MP5
printf "${GREEN}Installing packages for MP5...${NC}\n"
run_command pip3 install beautifulsoup4

# MP6 
printf "${GREEN}Installing packages for MP6...${NC}\n"
run_command pip3 install geopandas shapely descartes geopy netaddr==0.10.0

# MP7
printf "${GREEN}Installing packages for MP7...${NC}\n"
run_command pip3 install rasterio pillow scikit-learn

# Install Chromium
printf "${GREEN}Installing Chromium...${NC}\n"
run_command sudo apt-get install -y chromium-browser xdg-utils

# Install Chrome & WebDriver Manager dependencies
printf "${GREEN}Installing Chrome dependencies...${NC}\n"
run_command sudo apt-get install -y wget libasound2 libgbm1 libnspr4 libnss3 libu2f-udev libvulkan1 && sudo rm -rf /var/lib/apt/lists/*

# Ensure dpkg is configured properly
printf "${GREEN}Configuring dpkg if needed...${NC}\n"
run_command sudo dpkg --configure -a

# Download Google Chrome 
printf "${GREEN}Downloading Google Chrome...${NC}\n"
sudo wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
printf "${LIGHTGREEN}Installing...${NC}\n"
run_command sudo apt install ./google-chrome-stable_current_amd64.deb

# Extra Selenium requirements
printf "${GREEN}Installing extra Selenium requirements...${NC}\n"
run_command pip install webdriver-manager

# Clean up
printf "${GREEN}Cleaning up directory...${NC}\n"
run_command rm -f google-chrome-stable_current_amd64.deb

printf "${GREEN}All installations and configurations are complete.${NC}\n"
