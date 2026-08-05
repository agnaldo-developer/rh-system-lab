pipeline {
    agent {
        label 'devops-01'
    }

    options {
        disableConcurrentBuilds()
    }

    stages {
        stage('Identificar Agent') {
            steps {
                sh '''
                echo "Agent: $(hostname)"
                echo "Usuário: $(whoami)"
                echo "Workspace: $(pwd)"
                '''
            }
        }

        stage('Limpar Workspace') {
            steps {
                deleteDir()
            }
        }

stage('Checkout Git') {
    steps {
        checkout scm

        sh '''
            echo "Branch atual:"
            git branch --show-current

            echo "Último commit:"
            git log -1 --oneline

            echo "Origem configurada:"
            git remote -v
        '''
    }
}
        stage('Validar Checkout') {
            steps {
                sh '''
                echo "=================================="
                echo "Arquivos recebidos:"
                ls -lah

                echo
                echo "Branch atual:"
                git branch --show-current

                echo
                echo "Último commit:"
                git log -1 --oneline

                echo
                echo "Origem configurada:"
                git remote -v

                echo
                echo "Status do repositório:"
                git status --short
                echo "=================================="
                '''
            }
        }

        stage('Checkout Infraestrutura') {
            steps {
                dir('infra') {
                    git branch: 'main',
                    credentialsId: 'github-lab-devops-ssh',
                    url: 'git@github.com:agnaldo-developer/lab-devops.git'
                }
            }
        }
        stage('Testar Credencial Vault') {
            steps {
                withCredentials([
                string(
                credentialsId: 'ansible-vault-password',
                variable: 'ANSIBLE_VAULT_PASSWORD'
                )
                ]) {
                    sh '''
                    set -eu
                    set +x

                    VAULT_FILE="$WORKSPACE/.vault-test"

                    cleanup() {
                    rm -f "$VAULT_FILE"
                    }

                    trap cleanup EXIT

                    printf '%s' "$ANSIBLE_VAULT_PASSWORD" > "$VAULT_FILE"
                    chmod 600 "$VAULT_FILE"


                    /home/jenkins/ansible-venv/bin/ansible-vault view \
                    infra/ansible/inventories/azure/group_vars/azure_servers/vault.yml \
                    --vault-password-file "$VAULT_FILE" \
                    >/dev/null

                    echo "Os dois Vaults foram descriptografados pelo Jenkins"
                    '''
                }
            }
        }
        stage('Validar Repositório de Infraestrutura') {
            steps {
                sh '''
                set -eu

                echo "Branch da infraestrutura:"
                git -C infra branch --show-current

                echo
                echo "Último commit:"
                git -C infra log -1 --oneline

                echo
                echo "Estrutura principal:"
                find infra -maxdepth 2 -type d | sort

                echo
                echo "Dependências Ansible declaradas:"
                cat infra/ansible/requirements.yml
                '''
            }
        }

        stage('Preparar Ansible') {
            steps {
                sh '''
                set -eu

                ANSIBLE_BIN="/home/jenkins/ansible-venv/bin"

                echo "Versão do Ansible:"
                "$ANSIBLE_BIN/ansible" --version

                echo
                echo "Instalando collections do projeto:"
                "$ANSIBLE_BIN/ansible-galaxy" collection install \
                -r infra/ansible/requirements.yml

                echo
                echo "Collection community.docker:"
                "$ANSIBLE_BIN/ansible-galaxy" collection list |
                grep community.docker
                '''
            }
        }

        stage('Validar Estrutura Ansible') {
            steps {
                withCredentials([
                string(
                credentialsId: 'ansible-vault-password',
                variable: 'ANSIBLE_VAULT_PASSWORD'
                )
                ]) {
                    sh '''
                    set -eu
                    set +x

                    ANSIBLE_BIN="/home/jenkins/ansible-venv/bin"
                    VAULT_FILE="$WORKSPACE/.ansible-vault-${BUILD_NUMBER}"

                    cleanup_vault() {
                    rm -f "$VAULT_FILE"
                    }

                    trap cleanup_vault EXIT

                    printf '%s' "$ANSIBLE_VAULT_PASSWORD" > "$VAULT_FILE"
                    chmod 600 "$VAULT_FILE"

                    export ANSIBLE_VAULT_PASSWORD_FILE="$VAULT_FILE"

                    cd infra/ansible

                    echo "Playbooks encontrados:"
                    find playbooks \
                    -maxdepth 1 \
                    -type f \
                    -name '*.yml' \
                    | sort

                    echo
                    echo "Roles encontradas:"
                    find roles \
                    -mindepth 1 \
                    -maxdepth 1 \
                    -type d \
                    -printf '%f\\n' \
                    | sort

                    echo
                    echo "Inventário:"
                    "$ANSIBLE_BIN/ansible-inventory" \
                    -i inventories/azure/hosts.yml \
                    --graph
                    '''
                }
            }
        }
        stage('Testar Conectividade Azure') {
            steps {
                withCredentials([
                string(
                credentialsId: 'ansible-vault-password',
                variable: 'ANSIBLE_VAULT_PASSWORD'
                )
                ]) {
                    sshagent(credentials: ['ssh-azure-devops-01']) {
                        sh '''
                        set -eu
                        set +x

                        ANSIBLE_BIN="/home/jenkins/ansible-venv/bin"
                        VAULT_FILE="$WORKSPACE/.ansible-vault-${BUILD_NUMBER}"

                        cleanup_vault() {
                        rm -f "$VAULT_FILE"
                        }

                        trap cleanup_vault EXIT

                        printf '%s' "$ANSIBLE_VAULT_PASSWORD" > "$VAULT_FILE"
                        chmod 600 "$VAULT_FILE"

                        export ANSIBLE_VAULT_PASSWORD_FILE="$VAULT_FILE"
                        export ANSIBLE_SSH_COMMON_ARGS="-o StrictHostKeyChecking=accept-new"

                        cd infra/ansible

                        echo "Testando acesso à VM Azure..."

                        "$ANSIBLE_BIN/ansible" \
                        -i inventories/azure/hosts.yml \
                        azure_servers \
                        -m ping
                        '''
                    }
                }
            }
        }
        stage('Auditar Destino Azure') {
            steps {
                withCredentials([
                string(
                credentialsId: 'ansible-vault-password',
                variable: 'ANSIBLE_VAULT_PASSWORD'
                )
                ]) {
                    sshagent(credentials: ['ssh-azure-devops-01']) {
                        sh '''
                        set -eu
                        set +x

                        ANSIBLE_BIN="/home/jenkins/ansible-venv/bin"
                        VAULT_FILE="$WORKSPACE/.ansible-vault-${BUILD_NUMBER}"

                        cleanup_vault() {
                        rm -f "$VAULT_FILE"
                        }

                        trap cleanup_vault EXIT

                        printf '%s' "$ANSIBLE_VAULT_PASSWORD" > "$VAULT_FILE"
                        chmod 600 "$VAULT_FILE"

                        export ANSIBLE_VAULT_PASSWORD_FILE="$VAULT_FILE"
                        export ANSIBLE_SSH_COMMON_ARGS="-o StrictHostKeyChecking=accept-new"

                        cd infra/ansible

                        echo "Auditando a VM Azure..."

                        "$ANSIBLE_BIN/ansible-playbook" \
                        -i inventories/azure/hosts.yml \
                        playbooks/azure-deploy-audit.yml
                        '''
                    }
                }
            }
        }
 
        stage('Build da Imagem Docker') {
            steps {
                sh '''
                docker build \
                --tag rh-system-api:${BUILD_NUMBER} \
                --tag rh-system-api:latest \
                .
                '''
            }
        }
        stage('Validar Aplicação') {
            steps {
                sh '''
                    set -eu

                    echo "Validando arquivos obrigatórios..."

                    test -f Dockerfile
                    test -f compose.ci.yml
                    test -f requirements.txt
                    test -f pytest.ini
                    test -d app
                    test -d tests

                    echo "Validando sintaxe Python..."

                    python3 -m compileall app

                    echo "Validando Docker Compose de CI..."

                    docker compose \
                        -f compose.ci.yml \
                        config --quiet
                '''
            }
        }

        stage('Executar Testes de Integração') {
            steps {
                sh '''
                    set -eu

                    COMPOSE_PROJECT_NAME="rh-system-ci-${BUILD_NUMBER}"

                    echo "Construindo imagem de testes..."

                    docker compose \
                        -f compose.ci.yml \
                        -p "${COMPOSE_PROJECT_NAME}" \
                        build tests

                    echo "Executando os 18 testes..."

                    docker compose \
                        -f compose.ci.yml \
                        -p "${COMPOSE_PROJECT_NAME}" \
                        run --rm tests
                '''
            }
        }
        stage('Validar Imagem Docker') {
            steps {
                sh '''
                docker image ls rh-system-api

                docker image inspect \
                rh-system-api:${BUILD_NUMBER} \
                --format 'ID={{.Id}} Size={{.Size}} Created={{.Created}}'
                '''
            }
        }

        stage('Smoke Test da Imagem') {
            steps {
                sh '''
                set -eu

                CONTAINER_NAME="rh-system-smoke-${BUILD_NUMBER}"
                TEST_PORT="18000"

                cleanup() {
                docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
                }

                trap cleanup EXIT
                cleanup

                docker run -d \
                --name "${CONTAINER_NAME}" \
                --publish "127.0.0.1:${TEST_PORT}:8000" \
                --env APP_NAME="RH System API" \
                --env APP_ENV="test" \
                --env DATABASE_URL="sqlite:////tmp/rh-system-test.db" \
                "rh-system-api:${BUILD_NUMBER}"

                attempt=1

                until curl --fail --silent \
                "http://127.0.0.1:${TEST_PORT}/health" \
                > health-response.json
                do
                if [ "${attempt}" -ge 15 ]; then
                echo "Aplicação não ficou saudável."
                docker logs "${CONTAINER_NAME}" || true
                exit 1
                fi

                echo "Tentativa ${attempt}/15..."
                attempt=$((attempt + 1))
                sleep 2
                done

                cat health-response.json
                '''
            }
        }

        stage('Publicar Imagem no Docker Hub') {
            steps {
                withCredentials([
                usernamePassword(
                credentialsId: 'dockerhub-agnaldo',
                usernameVariable: 'DOCKERHUB_USERNAME',
                passwordVariable: 'DOCKERHUB_TOKEN'
                )
                ]) {
                    sh '''
                    set -eu
                    set +x

                    export DOCKER_CONFIG="$WORKSPACE/.docker-tmp"
                    mkdir -p "$DOCKER_CONFIG"

                    cleanup_registry_auth() {
                    docker logout >/dev/null 2>&1 || true
                    rm -rf "$DOCKER_CONFIG"
                    }

                    trap cleanup_registry_auth EXIT

                    IMAGE_REPOSITORY="${DOCKERHUB_USERNAME}/rh-system-api"
                    VERSION_TAG="${BUILD_NUMBER}"

                    printf '%s' "$DOCKERHUB_TOKEN" |
                    docker login \
                    --username "$DOCKERHUB_USERNAME" \
                    --password-stdin

                    docker tag \
                    "rh-system-api:${BUILD_NUMBER}" \
                    "${IMAGE_REPOSITORY}:${VERSION_TAG}"

                    docker tag \
                    "rh-system-api:${BUILD_NUMBER}" \
                    "${IMAGE_REPOSITORY}:latest"

                    docker push "${IMAGE_REPOSITORY}:${VERSION_TAG}"
                    docker push "${IMAGE_REPOSITORY}:latest"

                    echo "Publicação concluída:"
                    echo "${IMAGE_REPOSITORY}:${VERSION_TAG}"
                    echo "${IMAGE_REPOSITORY}:latest"
                    '''
                }
            }
        }// fecha Publicar Imagem no Docker Hub

        stage('[AZURE] Deploy na Cor Inativa') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'ansible-vault-password',
                        variable: 'ANSIBLE_VAULT_PASSWORD'
                    )
                ]) {
                    sshagent(credentials: ['ssh-azure-devops-01']) {
                        sh '''
                            set -eu
                            set +x

                            ANSIBLE_BIN="/home/jenkins/ansible-venv/bin"
                            VAULT_FILE="$WORKSPACE/.ansible-vault-${BUILD_NUMBER}"

                            cleanup_vault() {
                                rm -f "$VAULT_FILE"
                            }

                            trap cleanup_vault EXIT

                            printf '%s' "$ANSIBLE_VAULT_PASSWORD" > "$VAULT_FILE"
                            chmod 600 "$VAULT_FILE"

                            export ANSIBLE_VAULT_PASSWORD_FILE="$VAULT_FILE"
                            export ANSIBLE_SSH_COMMON_ARGS="-o StrictHostKeyChecking=accept-new"

                            cd infra/ansible

                            echo "Implantando imagem na cor inativa:"
                            echo "agnaldodeveloper/rh-system-api:${BUILD_NUMBER}"

                            "$ANSIBLE_BIN/ansible-playbook" \
                                -i inventories/azure/hosts.yml \
                                playbooks/azure-blue-green-deploy.yml \
                                --extra-vars \
                                "rh_system_api_tag=${BUILD_NUMBER}"
                        '''
                    }
                }
            }
        }

        stage('[AZURE] Aprovar Troca Blue/Green') {
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    input(
                        message: """
Ambiente: Azure

A nova imagem agnaldodeveloper/rh-system-api:${BUILD_NUMBER}
foi implantada e validada na cor inativa.

Deseja transferir o tráfego para a nova versão?
""",
                        ok: 'Promover na Azure'
                    )
                }
            }
        }

        stage('[AZURE] Trocar Tráfego Blue/Green') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'ansible-vault-password',
                        variable: 'ANSIBLE_VAULT_PASSWORD'
                    )
                ]) {
                    sshagent(credentials: ['ssh-azure-devops-01']) {
                        sh '''
                            set -eu
                            set +x

                            ANSIBLE_BIN="/home/jenkins/ansible-venv/bin"
                            VAULT_FILE="$WORKSPACE/.ansible-vault-${BUILD_NUMBER}"

                            cleanup_vault() {
                                rm -f "$VAULT_FILE"
                            }

                            trap cleanup_vault EXIT

                            printf '%s' "$ANSIBLE_VAULT_PASSWORD" > "$VAULT_FILE"
                            chmod 600 "$VAULT_FILE"

                            export ANSIBLE_VAULT_PASSWORD_FILE="$VAULT_FILE"
                            export ANSIBLE_SSH_COMMON_ARGS="-o StrictHostKeyChecking=accept-new"

                            cd infra/ansible

                            ACTIVE_COLOR=$(
                                "$ANSIBLE_BIN/ansible" \
                                    -i inventories/azure/hosts.yml \
                                    azure_servers \
                                    --become \
                                    -m ansible.builtin.command \
                                    -a "cat /opt/rh-system-blue-green/active-color" |
                                grep -E '^[[:space:]]*(blue|green)[[:space:]]*$' |
                                tail -1 |
                                xargs
                            )

                            case "$ACTIVE_COLOR" in
                                blue)
                                    TARGET_COLOR="green"
                                    ;;
                                green)
                                    TARGET_COLOR="blue"
                                    ;;
                                *)
                                    echo "Cor ativa inválida: $ACTIVE_COLOR"
                                    exit 1
                                    ;;
                            esac

                            echo "Cor atual: $ACTIVE_COLOR"
                            echo "Nova cor: $TARGET_COLOR"

                            "$ANSIBLE_BIN/ansible-playbook" \
                                -i inventories/azure/hosts.yml \
                                playbooks/azure-blue-green-switch.yml \
                                --extra-vars \
                                "target_color=${TARGET_COLOR}"
                        '''
                    }
                }
            }
        }

        stage('[AZURE] Validar Ambiente') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'ansible-vault-password',
                        variable: 'ANSIBLE_VAULT_PASSWORD'
                    )
                ]) {
                    sshagent(credentials: ['ssh-azure-devops-01']) {
                        sh '''
                            set -eu
                            set +x

                            ANSIBLE_BIN="/home/jenkins/ansible-venv/bin"
                            VAULT_FILE="$WORKSPACE/.ansible-vault-${BUILD_NUMBER}"

                            cleanup_vault() {
                                rm -f "$VAULT_FILE"
                            }

                            trap cleanup_vault EXIT

                            printf '%s' "$ANSIBLE_VAULT_PASSWORD" > "$VAULT_FILE"
                            chmod 600 "$VAULT_FILE"

                            export ANSIBLE_VAULT_PASSWORD_FILE="$VAULT_FILE"
                            export ANSIBLE_SSH_COMMON_ARGS="-o StrictHostKeyChecking=accept-new"

                            cd infra/ansible

                            echo "Validando aplicação através do Nginx..."

                            "$ANSIBLE_BIN/ansible" \
                                -i inventories/azure/hosts.yml \
                                azure_servers \
                                --become \
                                -m ansible.builtin.uri \
                                -a "url=http://127.0.0.1:18080/health status_code=200 return_content=true"

                            echo
                            echo "Estado final Blue/Green:"

                            "$ANSIBLE_BIN/ansible" \
                                -i inventories/azure/hosts.yml \
                                azure_servers \
                                --become \
                                -m ansible.builtin.shell \
                                -a 'echo -n "Cor ativa: "; \
                                    cat /opt/rh-system-blue-green/active-color; \
                                    echo; \
                                    echo "Upstream Nginx:"; \
                                    grep "server api-" /opt/rh-system-blue-green/nginx.conf; \
                                    echo; \
                                    echo -n "Imagem Blue: "; \
                                    docker container inspect rh-api-blue \
                                        --format="{% raw %}{{.Config.Image}}{% endraw %}"; \
                                    echo -n "Imagem Green: "; \
                                    docker container inspect rh-api-green \
                                        --format="{% raw %}{{.Config.Image}}{% endraw %}"'
                        '''
                    }
                }
            }
        }

        stage('[AZURE] Concluir Implantação') {
            steps {
                echo """
==================================================
AMBIENTE AZURE IMPLANTADO COM SUCESSO
==================================================
Imagem: agnaldodeveloper/rh-system-api:${BUILD_NUMBER}
Pipeline: ${BUILD_NUMBER}
Status: aprovado e validado
Estratégia: Blue/Green
==================================================
"""
            }
          }
       }
    post {
        success {
            echo 'CI/CD do RH System concluído com sucesso.'
        }

        failure {
            echo 'CI/CD do RH System falhou. Consulte o Console Output.'
        }

        always {
            sh '''
                set +e

                COMPOSE_PROJECT_NAME="rh-system-ci-${BUILD_NUMBER}"

                echo "Removendo ambiente temporário de testes..."

                docker compose \
                    -f compose.ci.yml \
                    -p "${COMPOSE_PROJECT_NAME}" \
                    down \
                    --volumes \
                    --remove-orphans \
                    || true
                echo "Limpando arquivos temporários..."

                rm -f test.db health-response.json || true
                rm -f "$WORKSPACE"/.ansible-vault-* || true
                rm -f "$WORKSPACE/.vault-test" || true
                rm -rf "$WORKSPACE/.docker-tmp" || true

                docker rm -f \
                    "rh-system-smoke-${BUILD_NUMBER}" \
                    >/dev/null 2>&1 || true

                echo "Uso final do workspace:"
                du -sh . || true
            '''
        }
    }
}
