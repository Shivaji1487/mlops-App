pipeline {
    agent any

    environment {
        DOCKER_HUB_USER        = 'sshivaji555'
        IMAGE_NAME             = 'mlops-app'
        IMAGE_TAG              = "v1.0.${BUILD_NUMBER}"
        
        // Centralized Endpoints
        MINIO_ENDPOINT         = 'http://192.168.235.130:9000'
        MLFLOW_S3_ENDPOINT_URL = 'http://192.168.235.130:9000'
        MLFLOW_TRACKING_URI    = 'http://192.168.235.130:5000'
        AWS_DEFAULT_REGION     = 'us-east-1'
        
        // MinIO Credentials Mapping
        MINIO_CREDS            = credentials('s3credentials')
        AWS_ACCESS_KEY_ID      = "${MINIO_CREDS_USR}"
        AWS_SECRET_ACCESS_KEY  = "${MINIO_CREDS_PSW}"
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
                    python -m pytest test/
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m src.train
                '''
            }
        }

        stage('Validate Model') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m src.validate
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

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'U', passwordVariable: 'P')]) {
                    sh 'echo "$P" | docker login -u "$U" --password-stdin'
                    sh 'docker push ' + DOCKER_HUB_USER + '/' + IMAGE_NAME + ':' + IMAGE_TAG
                    sh 'docker push ' + DOCKER_HUB_USER + '/' + IMAGE_NAME + ':latest'
                    sh 'docker logout'
                }
            }
        }

        stage('GitOps - Update Helm Chart') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                        sh '''
                            rm -rf mlops-gitops

                            git clone https://${GIT_USER}:${GIT_TOKEN}@github.com/Shivaji1487/mlops-gitops.git

                            cd mlops-gitops/applications/helm

                            git config user.name "Jenkins CI"
                            git config user.email "jenkins@local"

                            sed -i "s|repository: .*|repository: sshivaji555/mlops-app|g" values.yaml
                            sed -i "s|tag: .*|tag: ${IMAGE_TAG}|g" values.yaml

                            git add values.yaml

                            git commit -m "Deploy Image ${IMAGE_TAG}" || true

                            git remote set-url origin https://${GIT_USER}:${GIT_TOKEN}@github.com/Shivaji1487/mlops-gitops.git

                            git push origin main
                        '''
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