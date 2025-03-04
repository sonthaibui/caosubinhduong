# Use the official Odoo image as the base image
FROM odoo:15.0

# Install additional tools
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    vim \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Create the vscode user if it doesn't exist
RUN id -u vscode &>/dev/null || useradd -m -s /bin/bash vscode

# Switch to the vscode user
USER vscode

# Set up the working directory to where Odoo expects custom add-ons
WORKDIR /mnt/extra-addons

# Copy your add-on to the working directory
COPY . /mnt/extra-addons

# Expose Odoo port (default is 8069)
EXPOSE 8069