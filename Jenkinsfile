pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()

        buildDiscarder(
            logRotator(
                numToKeepStr: '10',
                artifactNumToKeepStr: '5'
            )
        )
    }

    environment {
        APP_NAME = 'rh-system'
        APP_VERSION = "0.1.${BUILD_NUMBER}"
        RELEASE_IMAGE = "${APP_NAME}:${APP_VERSION}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm

                sh '''
                    echo "Branch em execução:"
                    git branch --show-current

                    echo "Commit em execução:"
                    git log -1 --oneline
                '''
            }
        }

        stage('Validar Estrutura') {
            steps {
                sh '''
                    set -eu

                    echo "Validando arquivos obrigatórios..."

                    test -f Dockerfile
                    test -f docker-compose.yml
                    test -f requirements.txt
                    test -f pytest.ini
                    test -d app
                    test -d tests

                    echo "Validando sintaxe do Docker Compose..."

                    docker compose config --quiet
                '''
            }
        }

        stage('Build Testes') {
            steps {
                sh '''
                    set -eu

                    echo "Construindo imagem utilizada nos testes..."

                    docker compose build tests
                '''
            }
        }

        stage('Testes Automatizados') {
            steps {
                sh '''
                    set -eu

                    echo "Executando testes de integração..."

                    docker compose run --rm tests
                '''
            }
        }

        stage('Build Imagem Release') {
            steps {
                sh '''
                    set -eu

                    echo "Construindo imagem de entrega: ${RELEASE_IMAGE}"

                    docker build \
                      --tag "${RELEASE_IMAGE}" \
                      --label "org.opencontainers.image.revision=${GIT_COMMIT}" \
                      --label "org.opencontainers.image.version=${APP_VERSION}" \
                      .
                '''
            }
        }

        stage('Validar Imagem') {
            steps {
                sh '''
                    set -eu

                    echo "Imagem criada:"

                    docker image inspect "${RELEASE_IMAGE}" \
                      --format='ID={{.Id}} Criada={{.Created}}'

                    echo "Comando configurado na imagem:"

                    docker image inspect "${RELEASE_IMAGE}" \
                      --format='{{json .Config.Cmd}}'
                '''
            }
        }
    }

    post {
        always {
            sh '''
                echo "Limpando containers e banco temporário de testes..."

                docker compose down \
                  --volumes \
                  --remove-orphans \
                  || true
            '''
        }

        success {
            echo "CI concluída com sucesso. Imagem criada: ${RELEASE_IMAGE}"
        }

        failure {
            echo 'CI falhou. Nenhuma versão deve avançar para deploy.'
        }
    }
}
