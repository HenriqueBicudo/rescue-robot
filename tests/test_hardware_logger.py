"""Testes pytest para os módulos robot/hardware e robot/logger."""

import pytest
import tempfile
import os
from simulator.map_loader import load_map
from simulator.simulator import Simulator, InvalidPickupError
from robot.hardware import HardwareInterface
from robot.logger import Logger


class TestLogger:
    """Testes para o Logger."""
    
    def test_logger_creates_csv_file(self):
        """Testa se o logger cria arquivo CSV."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Muda para o diretório temporário
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                logger = Logger("test_map.txt")
                logger.log("LIGAR", "PAREDE", "VAZIO", "HUMANO", False)
                logger.close()
                
                # Verifica se arquivo foi criado
                assert os.path.exists("test_map.csv")
                
                # Verifica conteúdo
                with open("test_map.csv", 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert content == "LIGAR,PAREDE,VAZIO,HUMANO,SEM CARGA\n"
            finally:
                os.chdir(original_cwd)
    
    def test_logger_without_txt_extension(self):
        """Testa logger com nome sem extensão .txt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                logger = Logger("map1")
                logger.log("A", "VAZIO", "VAZIO", "PAREDE", True)
                logger.close()
                
                assert os.path.exists("map1.csv")
                
                with open("map1.csv", 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert content == "A,VAZIO,VAZIO,PAREDE,COM HUMANO\n"
            finally:
                os.chdir(original_cwd)
    
    def test_logger_multiple_entries(self):
        """Testa múltiplas entradas no log."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                logger = Logger("test")
                logger.log("LIGAR", "PAREDE", "VAZIO", "VAZIO", False)
                logger.log("A", "PAREDE", "VAZIO", "HUMANO", False)
                logger.log("P", "PAREDE", "VAZIO", "VAZIO", True)
                logger.close()
                
                with open("test.csv", 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    assert len(lines) == 3
                    assert lines[0] == "LIGAR,PAREDE,VAZIO,VAZIO,SEM CARGA\n"
                    assert lines[1] == "A,PAREDE,VAZIO,HUMANO,SEM CARGA\n"
                    assert lines[2] == "P,PAREDE,VAZIO,VAZIO,COM HUMANO\n"
            finally:
                os.chdir(original_cwd)


class TestHardwareInterface:
    """Testes para o HardwareInterface."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Criar mapa temporário com entrada na borda inferior (para direção Norte)
        self.map_content = "XXXXX\nX...X\nX.@.X\nX...X\nX.E.X"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(self.map_content)
            self.map_path = f.name
        
        # Carregar mapa e criar simulador
        self.grid = load_map(self.map_path)
        self.simulator = Simulator(self.grid)
        
        # Mudar para diretório temporário para arquivos CSV
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        # Fechar hardware se existir para liberar arquivos
        if hasattr(self, 'hardware'):
            self.hardware.close()
            
        # Voltar ao diretório original
        os.chdir(self.original_cwd)
        
        # Remover arquivos temporários
        if os.path.exists(self.map_path):
            os.unlink(self.map_path)
        
        # Limpar diretório temporário
        import time
        time.sleep(0.1)  # Pequena pausa para garantir que arquivos sejam liberados
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                try:
                    os.unlink(file_path)
                except PermissionError:
                    pass  # Ignorar se arquivo ainda estiver em uso
            os.rmdir(self.temp_dir)
        except (OSError, PermissionError):
            pass  # Ignorar erros de cleanup
    
    def test_hardware_creates_csv_with_ligar_line(self):
        """Testa se HardwareInterface cria CSV com linha LIGAR."""
        map_filename = os.path.basename(self.map_path)
        hardware = HardwareInterface(self.simulator, map_filename)
        
        # Verificar se arquivo CSV foi criado
        expected_csv = map_filename.replace('.txt', '.csv')
        assert os.path.exists(expected_csv)
        
        # Verificar conteúdo
        with open(expected_csv, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 1
            
            # Linha deve começar com LIGAR e terminar com SEM CARGA
            line = lines[0].strip()
            parts = line.split(',')
            assert parts[0] == "LIGAR"
            assert parts[4] == "SEM CARGA"
        
        hardware.close()
    
    def test_hardware_initial_position_and_direction(self):
        """Testa posição e direção inicial do hardware."""
        map_filename = os.path.basename(self.map_path)
        hardware = HardwareInterface(self.simulator, map_filename)
        self.hardware = hardware  # Para cleanup
        
        # Posição inicial deve ser a entrada (2, 4)
        assert hardware.pos == (2, 4)
        
        # Direção deve ser Norte (0) pois entrada está na borda inferior
        assert hardware.dir == 0
        
        # Carga inicial deve ser False
        assert hardware.carga == False
    
    def test_hardware_send_command_creates_new_line(self):
        """Testa se send_command cria nova linha no CSV."""
        map_filename = os.path.basename(self.map_path)
        hardware = HardwareInterface(self.simulator, map_filename)
        self.hardware = hardware  # Para cleanup
        
        # Enviar comando A (avançar) - na direção Norte
        left, right, front, carga = hardware.send_command('A')
        
        # Verificar arquivo CSV
        expected_csv = map_filename.replace('.txt', '.csv')
        with open(expected_csv, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 2  # LIGAR + A
            
            # Segunda linha deve ser do comando A
            line = lines[1].strip()
            parts = line.split(',')
            assert parts[0] == "A"
            assert parts[4] == "SEM CARGA"  # Ainda sem carga
    
    def test_hardware_invalid_pickup_no_csv_line(self):
        """Testa que comando P inválido não cria linha no CSV."""
        map_filename = os.path.basename(self.map_path)
        hardware = HardwareInterface(self.simulator, map_filename)
        self.hardware = hardware  # Para cleanup
        
        # Tentar pegar humano quando não há humano na frente
        with pytest.raises(InvalidPickupError):
            hardware.send_command('P')
        
        # Verificar que não foi criada linha adicional
        expected_csv = map_filename.replace('.txt', '.csv')
        with open(expected_csv, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 1  # Apenas LIGAR
        
        # Verificar que carga não mudou
        assert hardware.carga == False
    
    def test_hardware_successful_pickup(self):
        """Testa comando P bem-sucedido."""
        # Usar um mapa mais simples onde é fácil pegar o humano
        simple_content = "XXX\nE@X\nXXX"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(simple_content)
            simple_map_path = f.name
        
        try:
            grid = load_map(simple_map_path)
            simulator = Simulator(grid)
            
            map_filename = os.path.basename(simple_map_path)
            hardware = HardwareInterface(simulator, map_filename)
            self.hardware = hardware  # Para cleanup
            
            # Na entrada (0, 1) direção Leste, humano está em (1, 1)
            # Pegar o humano diretamente
            left, right, front, carga = hardware.send_command('P')
            
            # Verificar que carga agora é True
            assert carga == True
            assert hardware.carga == True
            
            # Verificar linha no CSV
            expected_csv = map_filename.replace('.txt', '.csv')
            with open(expected_csv, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Última linha deve ter COM HUMANO
                last_line = lines[-1].strip()
                parts = last_line.split(',')
                assert parts[0] == "P"
                assert parts[4] == "COM HUMANO"
                
        finally:
            if os.path.exists(simple_map_path):
                os.unlink(simple_map_path)
    
    def test_hardware_read_sensors(self):
        """Testa leitura dos sensores."""
        map_filename = os.path.basename(self.map_path)
        hardware = HardwareInterface(self.simulator, map_filename)
        self.hardware = hardware  # Para cleanup
        
        # Verificar as leituras dos sensores na posição inicial
        left, right, front = hardware.read_sensors()
        
        # Como hardware é criado dinamicamente, vamos verificar se retorna valores válidos
        valid_readings = {'PAREDE', 'VAZIO', 'HUMANO'}
        assert left in valid_readings
        assert right in valid_readings
        assert front in valid_readings


if __name__ == "__main__":
    pytest.main([__file__])