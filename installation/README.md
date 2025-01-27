# Dependency Installation

This directory contains the following file: `cs-320-requirements.sh`. These file will help you with the installation of all of the python libraries and dependencies that you will be using throughout the semester. 

### Running the shell script 
Running this script will ensure that all of the necessary dependencies are installed. To execute the script, simply run the folliwing command:

```{bash}
./cs-320-requirements.sh
```

**Note:** if after attempting to run the script, you get the following error: `bash: ./cs-320-requirements.sh: Permission denied`. Then you will need to run: `chmod +x cs-320-requirements.sh` prior to executing the script again. The reason this happens is because in Unix-like operating systems (including Ubuntu/Linux), every file has a set of permissions that determine who can read, write, or execute the file. Running this the command mentioned above will ensure that you have the correct permissions to execute the script.