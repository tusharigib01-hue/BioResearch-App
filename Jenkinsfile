pipeline {
    agent any

    stages {

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t bioresearch-app .'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh 'docker stop bioresearch-container || true'
                sh 'docker rm bioresearch-container || true'
            }
        }

        stage('Deploy Container') {
            steps {
                sh 'docker run -d -p 5050:5000 --name bioresearch-container bioresearch-app'
            }
        }

    }
}
