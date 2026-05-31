pipeline {
    agent any

    stages {

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t lostfound .'
            }
        }

        stage('Save Docker Image') {
            steps {
                bat 'docker save -o lostfound.tar lostfound'
            }
        }

        stage('Deploy to EC2') {
            steps {
                bat 'scp -i C:\\jenkins-keys\\id_ed25519 -o StrictHostKeyChecking=no lostfound.tar ubuntu@34.224.80.158:/home/ubuntu/'

                bat 'ssh -i C:\\jenkins-keys\\id_ed25519 -o StrictHostKeyChecking=no ubuntu@34.224.80.158 "sudo docker load -i /home/ubuntu/lostfound.tar"'

                bat 'ssh -i C:\\jenkins-keys\\id_ed25519 -o StrictHostKeyChecking=no ubuntu@34.224.80.158 "sudo docker stop lostfound || true"'

                bat 'ssh -i C:\\jenkins-keys\\id_ed25519 -o StrictHostKeyChecking=no ubuntu@34.224.80.158 "sudo docker rm lostfound || true"'

                bat 'ssh -i C:\\jenkins-keys\\id_ed25519 -o StrictHostKeyChecking=no ubuntu@34.224.80.158 "sudo docker run -d --name lostfound -p 8501:8501 lostfound"'
            }
        }
        }
    }
}