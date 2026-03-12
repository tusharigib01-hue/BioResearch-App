pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "tusharban01/bioresearch-app"
        CONTAINER_NAME = "bioresearch-container"
    }

    stages {

        stage('Clone Repository') {
            steps {
                git 'https://github.com/tusharigib01-hue/BioResearch-App.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:latest .'
            }
        }

        stage('Push Image to DockerHub') {
            steps {
                sh 'docker push $DOCKER_IMAGE:latest'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh 'docker stop $CONTAINER_NAME || true'
                sh 'docker rm $CONTAINER_NAME || true'
            }
        }

        stage('Deploy Container') {
            steps {
                sh 'docker run -d -p 5050:5000 --name $CONTAINER_NAME $DOCKER_IMAGE:latest'
            }
        }
    }
}
