pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'shivaji1487'
        IMAGE_NAME      = 'mlops-app'
        IMAGE_TAG       = "v1.0.${BUILD_NUMBER}"
        GITOPS_REPO     = 'github.com/Shivaji1487/mlops-gitops.git'
		
		// Centralized Endpoints
        MINIO_ENDPOINT         = 'http://192.168.235.130:9000'
        MLFLOW_S3_ENDPOINT_URL = 'http://192.168.235.130:9000'
        MLFLOW_TRACKING_URI    = 'http://192.168.235.130:5000'
		
		// MinIO Credentials fetched safely from Jenkins Credentials Store
        AWS_ACCESS_KEY_ID     = credentials('s3credentials_USR')
        AWS_SECRET_ACCESS_KEY = credentials('s3credentials_PSW')
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest test/
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                    . venv/bin/activate
                    python src/train.py
                '''
            }
        }

        stage('Validate Model') {
            steps {
                sh '''
                    . venv/bin/activate
                    python src/validate.py
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG} .
                    docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                            docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}
                            docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest
                        """
                    }
                }
            }
        }

        stage('GitOps - Update Helm Chart') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                        sh """
                            rm -rf mlops-gitops
                            git clone https://${GIT_USER}:${GIT_TOKEN}@${GITOPS_REPO}
                            
                            cd mlops-gitops/applications/helm
                            
                            # Update image tag in values.yaml
                            sed -i 's/tag: .*/tag: "${IMAGE_TAG}"/' values.yaml
                            
                            git config user.email "jenkins@ci.com"
                            git config user.name "Jenkins CI"
                            
                            git add values.yaml
                            git commit -m "chore(gitops): update image tag to ${IMAGE_TAG} [skip ci]"
                            git push origin main
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}