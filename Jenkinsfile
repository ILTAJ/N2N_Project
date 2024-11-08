pipeline {
    agent any
    options {
        // Shorter timeout since we have limited resources
        timeout(time: 30, unit: 'MINUTES')
    }
    environment {
        DOCKER_REGISTRY = 'localhost:5000'
        IMAGE_NAME = 'cats-dogs-model-server'
        // Very conservative memory limits for Docker
        DOCKER_BUILD_OPTS = '--memory=384m --memory-swap=768m'
    }
    stages {
        // Always clean before building to free up resources
        stage('Cleanup') {
            steps {
                sh '''
                    docker system prune -af --volumes
                    docker image prune -af
                    docker container prune -f
                '''
            }
        }
        stage('Build') {
            steps {
                script {
                    // Stop any running containers before building
                    sh 'docker-compose down || true'
                    docker.build("${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}", "${DOCKER_BUILD_OPTS} .")
                }
            }
        }
        stage('Deploy') {
            steps {
                // Remove the push stage since we're using localhost registry
                sh 'docker-compose down'
                sh 'docker-compose up -d'
            }
        }
    }
    post {
        always {
            cleanWs()
            sh 'docker system prune -af || true'
        }
    }
}