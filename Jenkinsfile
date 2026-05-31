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
                sshPublisher(
                    publishers: [
                        sshPublisherDesc(
                            configName: 'ec2',
                            transfers: [
                                sshTransfer(
                                    sourceFiles: 'lostfound.tar',
                                    remoteDirectory: '',
                                    execCommand: '''
sudo docker load -i /home/ubuntu/lostfound.tar
sudo docker stop lostfound || true
sudo docker rm lostfound || true
sudo docker run -d --name lostfound -p 8501:8501 lostfound
'''
                                )
                            ]
                        )
                    ]
                )
            }
        }
    }
}