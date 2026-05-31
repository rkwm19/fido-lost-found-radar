pipeline {
    agent any

    stages {
        stage('Test SSH') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    bat 'ssh -o StrictHostKeyChecking=no ubuntu@34.224.80.158 "echo SSH_WORKS"'
                }
            }
        }
    }
}