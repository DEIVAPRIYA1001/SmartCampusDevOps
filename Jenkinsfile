pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat 'pytest'
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker build -t smart-campus .'
            }
        }

        stage('Ansible Deployment') {
            steps {
                bat 'wsl -d Ubuntu ansible-playbook -i /root/smart-campus-ansible/inventory /root/smart-campus-ansible/deploy.yml'
            }
        }
    }
}