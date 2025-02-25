# Define variables
$repositoryPath = "C:\rubber15\server\rubber"
$gitExecutable = "C:\Program Files\Git\bin\git.exe"

# Navigate to the repository
cd $repositoryPath

# Pull the latest changes
& $gitExecutable pull origin main

# Restart Odoo service
Restart-Service -Name "odoo-server-15.0"