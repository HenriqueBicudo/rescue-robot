# 📦 INSTRUÇÕES DE EMPACOTAMENTO - RESGATE ROBOT

Este documento contém instruções passo-a-passo para empacotar e submeter o trabalho de Serviços Cognitivos.

## 🎯 Objetivo
Os scripts `package_submission.sh` (Linux/macOS) e `package_submission.py` (multiplataforma) automatizam:
- ✅ Verificação de arquivos obrigatórios (TEAM.txt, mapas)
- ✅ Execução automática de testes
- ✅ Criação de ZIP de submissão
- ✅ Validação de estrutura de projeto

## 🐧 LINUX/macOS - Usando Bash Script

### Pré-requisitos
```bash
# Verificar se você tem os requisitos
python3 --version  # Python 3.x necessário
pip3 --version     # pip para instalar pytest
```

### Passo-a-Passo

#### 1. Navegue para o diretório do projeto
```bash
cd /caminho/para/resgate-robot
# Certifique-se de que você está no diretório onde está o README.md
ls -la README.md simulator/ robot/ controller/
```

#### 2. Torne o script executável
```bash
chmod +x package_submission.sh
```

#### 3. Execute o script
```bash
./package_submission.sh
```

### Saída Esperada
```
==========================================
🤖 PACKAGE SUBMISSION - RESGATE ROBOT 🤖
==========================================
[INFO] Diretório correto identificado: /path/to/resgate-robot
[✓] TEAM.txt encontrado
[✓] Matrícula do líder identificada: 123456789
[✓] Encontrados 3 mapas (mínimo: 3)
[✓] Python encontrado: Python 3.10.6
[✓] pytest disponível
Aguarde, executando testes...
[✓] Todos os testes passaram!
[✓] Estrutura de diretórios validada
[INFO] Criando arquivo de submissão: trabalho_servicos_cognitivos_123456789.zip
[✓] Arquivo criado: trabalho_servicos_cognitivos_123456789.zip
==========================================
✅ EMPACOTAMENTO CONCLUÍDO COM SUCESSO!
==========================================
```

## 🪟 WINDOWS/LINUX/macOS - Usando Python Script

### Pré-requisitos
```bash
# Windows (PowerShell/CMD)
python --version
pip --version

# Linux/macOS
python3 --version
pip3 --version
```

### Passo-a-Passo

#### 1. Navegue para o diretório do projeto
```bash
# Windows
cd C:\path\to\resgate-robot

# Linux/macOS
cd /path/to/resgate-robot
```

#### 2. Execute o script Python
```bash
# Windows
python package_submission.py

# Linux/macOS (se python3 for necessário)
python3 package_submission.py
```

## 🔧 Solução de Problemas

### ❌ Erro: "Execute este script no diretório raiz"
**Solução:** Navegue para o diretório onde estão os arquivos README.md e as pastas simulator/, robot/, etc.
```bash
cd resgate-robot/
ls README.md  # Deve existir
```

### ❌ Erro: "TEAM.txt não encontrado"
**Solução:** Crie/verifique o arquivo TEAM.txt com a matrícula do líder na primeira linha:
```bash
echo "123456789 - João Silva" > TEAM.txt
```

### ❌ Erro: "Encontrados apenas X mapas. Mínimo necessário: 3"
**Solução:** Adicione mais mapas na pasta maps/:
```bash
ls maps/*.txt  # Deve mostrar pelo menos 3 arquivos
```

### ❌ Erro: "pytest não encontrado"
**Solução:** Instale pytest:
```bash
# Windows
pip install pytest

# Linux/macOS
pip3 install pytest
```

### ❌ Erro: "Alguns testes falharam"
**Solução:** Execute testes detalhados para ver os erros:
```bash
# Windows
python -m pytest tests/ -v

# Linux/macOS
python3 -m pytest tests/ -v
```

### ❌ Erro: "zip não encontrado" (Linux)
**Solução:** Instale zip ou use a versão tar.gz:
```bash
# Ubuntu/Debian
sudo apt-get install zip

# CentOS/RHEL
sudo yum install zip

# O script automaticamente usa tar.gz como fallback
```

## 📋 Checklist Final

Antes de submeter, verifique:

- [ ] ✅ Arquivo ZIP criado com sucesso
- [ ] ✅ Nome do arquivo: `trabalho_servicos_cognitivos_<matricula>.zip`
- [ ] ✅ Todos os testes passaram
- [ ] ✅ Estrutura de diretórios completa:
  - [ ] simulator/
  - [ ] robot/
  - [ ] controller/
  - [ ] algorithms/
  - [ ] tests/
  - [ ] maps/ (mínimo 3 arquivos .txt)
- [ ] ✅ Arquivos essenciais incluídos:
  - [ ] TEAM.txt
  - [ ] README.md
  - [ ] Todos os arquivos .py

## 🎉 Submissão

1. **Localize o arquivo ZIP:** `trabalho_servicos_cognitivos_<matricula>.zip`
2. **Verifique o tamanho:** Deve ter alguns MB com todo o código
3. **Teste o ZIP:** Extraia em local temporário e verifique se tudo está lá
4. **Submeta na plataforma:** Upload do arquivo ZIP na plataforma de entrega
5. **Confirme:** Aguarde confirmação de recebimento

## 🚨 Importante

- **NÃO modifique** os arquivos após gerar o ZIP
- **Mantenha backup** do projeto
- **Teste o ZIP** antes de submeter (extraia e verifique)
- **Submeta antes do prazo** final

## 📞 Suporte

Se encontrar problemas:
1. Verifique esta documentação
2. Execute os comandos de diagnóstico sugeridos
3. Verifique se todos os pré-requisitos estão instalados
4. Entre em contato com a equipe se necessário

---
**Boa sorte! 🤖✨**