#!/bin/bash

# package_submission.sh
# Script para empacotamento automático do trabalho de Serviços Cognitivos
# Autor: Equipe Resgate Robot
# Data: 16/09/2025

set -e  # Para no primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "=========================================="
echo "🤖 PACKAGE SUBMISSION - RESGATE ROBOT 🤖"
echo "=========================================="
echo -e "${NC}"

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Verificar se estamos no diretório correto
if [ ! -f "README.md" ] || [ ! -d "simulator" ]; then
    log_error "Execute este script no diretório raiz do projeto (onde está o README.md)"
    exit 1
fi

log_info "Diretório correto identificado: $(pwd)"

# 1. Verificar existência de TEAM.txt
log_info "Verificando arquivo TEAM.txt..."
if [ ! -f "TEAM.txt" ]; then
    log_error "Arquivo TEAM.txt não encontrado!"
    exit 1
fi
log_success "TEAM.txt encontrado"

# Extrair matrícula do líder do TEAM.txt
MATRICULA_LEADER=$(head -1 TEAM.txt | grep -o '[0-9]\+' | head -1)
if [ -z "$MATRICULA_LEADER" ]; then
    log_warning "Matrícula não encontrada em TEAM.txt. Usando 'UNKNOWN'"
    MATRICULA_LEADER="UNKNOWN"
else
    log_success "Matrícula do líder identificada: $MATRICULA_LEADER"
fi

# 2. Verificar mapas em maps/
log_info "Verificando mapas em maps/..."
if [ ! -d "maps" ]; then
    log_error "Diretório maps/ não encontrado!"
    exit 1
fi

MAP_COUNT=$(find maps/ -name "*.txt" -type f | wc -l)
if [ "$MAP_COUNT" -lt 3 ]; then
    log_error "Encontrados apenas $MAP_COUNT mapas. Mínimo necessário: 3"
    log_info "Mapas encontrados:"
    find maps/ -name "*.txt" -type f | sed 's/^/  - /'
    exit 1
fi
log_success "Encontrados $MAP_COUNT mapas (mínimo: 3)"

# 3. Verificar se Python está disponível
log_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        log_error "Python não encontrado! Instale Python 3.x"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi
log_success "Python encontrado: $($PYTHON_CMD --version)"

# 4. Verificar se pytest está instalado
log_info "Verificando pytest..."
if ! $PYTHON_CMD -m pytest --version &> /dev/null; then
    log_warning "pytest não encontrado. Tentando instalar..."
    $PYTHON_CMD -m pip install pytest
    if [ $? -ne 0 ]; then
        log_error "Falha ao instalar pytest. Instale manualmente: pip install pytest"
        exit 1
    fi
fi
log_success "pytest disponível"

# 5. Executar testes
log_info "Executando testes com pytest..."
echo -e "${YELLOW}Aguarde, executando testes...${NC}"

if $PYTHON_CMD -m pytest tests/ -q --tb=short; then
    log_success "Todos os testes passaram!"
else
    log_error "Alguns testes falharam. Corrija os problemas antes de submeter."
    echo -e "${YELLOW}Para ver detalhes dos erros, execute:${NC}"
    echo "  $PYTHON_CMD -m pytest tests/ -v"
    exit 1
fi

# 6. Verificar estrutura de diretórios obrigatória
log_info "Verificando estrutura de diretórios..."
REQUIRED_DIRS=("simulator" "robot" "controller" "algorithms" "tests" "maps")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        log_error "Diretório obrigatório '$dir' não encontrado!"
        exit 1
    fi
done
log_success "Estrutura de diretórios validada"

# 7. Criar arquivo ZIP
ZIP_NAME="trabalho_servicos_cognitivos_${MATRICULA_LEADER}.zip"
log_info "Criando arquivo de submissão: $ZIP_NAME"

# Remover ZIP anterior se existir
if [ -f "$ZIP_NAME" ]; then
    rm "$ZIP_NAME"
    log_info "Arquivo ZIP anterior removido"
fi

# Criar lista de arquivos para incluir
INCLUDE_PATTERNS=(
    "*.py"
    "*.txt" 
    "*.md"
    "simulator/"
    "robot/"
    "controller/"
    "algorithms/"
    "tests/"
    "maps/"
)

# Criar ZIP excluindo arquivos desnecessários
if command -v zip &> /dev/null; then
    # Usar zip se disponível
    zip -r "$ZIP_NAME" . \
        -i "${INCLUDE_PATTERNS[@]}" \
        -x "*.pyc" "*__pycache__*" "*.pytest_cache*" "*/.git*" "*.gitignore*" \
        > /dev/null 2>&1
else
    # Fallback para tar
    log_warning "zip não encontrado, usando tar.gz"
    ZIP_NAME="trabalho_servicos_cognitivos_${MATRICULA_LEADER}.tar.gz"
    tar -czf "$ZIP_NAME" \
        --exclude="*.pyc" \
        --exclude="__pycache__" \
        --exclude=".pytest_cache" \
        --exclude=".git" \
        --exclude=".gitignore" \
        simulator/ robot/ controller/ algorithms/ tests/ maps/ *.py *.txt *.md
fi

if [ -f "$ZIP_NAME" ]; then
    log_success "Arquivo criado: $ZIP_NAME"
    
    # Mostrar informações do arquivo
    if command -v du &> /dev/null; then
        SIZE=$(du -h "$ZIP_NAME" | cut -f1)
        log_info "Tamanho do arquivo: $SIZE"
    fi
    
    # Listar conteúdo do ZIP
    log_info "Conteúdo do arquivo:"
    if [[ "$ZIP_NAME" == *.zip ]]; then
        if command -v unzip &> /dev/null; then
            unzip -l "$ZIP_NAME" | head -20
        fi
    else
        tar -tzf "$ZIP_NAME" | head -20
    fi
    
else
    log_error "Falha ao criar arquivo de submissão"
    exit 1
fi

# 8. Resumo final
echo ""
echo -e "${GREEN}=========================================="
echo "✅ EMPACOTAMENTO CONCLUÍDO COM SUCESSO!"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}📁 Arquivo de submissão:${NC} $ZIP_NAME"
echo -e "${BLUE}🎯 Matrícula do líder:${NC} $MATRICULA_LEADER"
echo -e "${BLUE}🗺️  Mapas encontrados:${NC} $MAP_COUNT"
echo -e "${BLUE}🧪 Testes:${NC} Todos passaram"
echo ""
echo -e "${YELLOW}📋 PRÓXIMOS PASSOS:${NC}"
echo "1. Verifique o arquivo $ZIP_NAME"
echo "2. Submeta este arquivo na plataforma de entrega"
echo "3. Mantenha uma cópia de backup"
echo ""
echo -e "${GREEN}🎉 Trabalho pronto para submissão!${NC}"