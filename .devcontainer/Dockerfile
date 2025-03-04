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

# Switch back to the odoo user
USER odoo

# Set up the working directory
WORKDIR /mnt/extra-addons

# Copy your add-on to the working directory
COPY . /mnt/extra-addons

# Expose Odoo port
EXPOSE 8069