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
                sshagent(credentials: ['ec2-ssh-key']) {

                    bat 'scp -o StrictHostKeyChecking=no lostfound.tar ubuntu@34.224.80.158:/home/ubuntu/'

                    bat 'ssh -o StrictHostKeyChecking=no ubuntu@34.224.80.158 "sudo docker load -i /home/ubuntu/lostfound.tar"'

                    bat 'ssh -o StrictHostKeyChecking=no ubuntu@34.224.80.158 "sudo docker stop lostfound || true"'

                    bat 'ssh -o StrictHostKeyChecking=no ubuntu@34.224.80.158 "sudo docker rm lostfound || true"'

                    bat 'ssh -o StrictHostKeyChecking=no ubuntu@34.224.80.158 "sudo docker run -d --name lostfound -p 8501:8501 lostfound"'
                }
            }
        }
    }
}