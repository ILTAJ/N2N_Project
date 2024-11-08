pipeline {
    agent any
    environment {
    DOCKER_REGISTRY = 'localhost:5000'
    IMAGE_NAME = 'cats-dogs-model-server'
}
    stages {
        stage('Build') {
            steps {
                script {
                    docker.build("${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}")
                }
            }
        }
        stage('Push to Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'DOCKER_CREDENTIALS_ID', passwordVariable: 'dockerpwd', usernameVariable: 'docker_username')]) {
                    sh 'echo $dockerpwd | docker login -u $docker_username --password-stdin ${DOCKER_REGISTRY}'
                    sh 'docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}'
                    sh 'docker logout'
                }
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker-compose down'
                sh 'docker-compose up -d'
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}