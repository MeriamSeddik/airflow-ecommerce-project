FROM jenkins/jenkins:lts
USER root
# Installation du client Docker
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*
# Ajout de l'utilisateur jenkins au groupe docker pour avoir les droits d'exécution
RUN usermod -aG docker jenkins
USER jenkins