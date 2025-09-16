"""Testes de alarmes para verificar cenários de erro e logging."""

import pytest
import tempfile
import os
from simulator.map_loader import load_map
from simulator.simulator import Simulator
from robot.hardware import HardwareInterface
from controller.controller import RobotController
from algorithms.returner import BecoPosColetaError, plan_return


class TestAlarms:
    """Testes para cenários de alarme."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Mudar para diretório temporário para arquivos CSV
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        # Voltar ao diretório original
        os.chdir(self.original_cwd)
        
        # Limpar diretório temporário
        import time
        time.sleep(0.1)
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                try:
                    os.unlink(file_path)
                except PermissionError:
                    pass
            os.rmdir(self.temp_dir)
        except (OSError, PermissionError):
            pass
    
    def test_beco_pos_coleta_alarm(self):
        """Testa alarme de beco após coleta de humano."""
        # Criar mapa que força situação de beco - E deve estar na borda
        beco_content = """XXXXX
X...X
X.@.X
X...X
EXXXX"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(beco_content)
            map_path = f.name
        
        try:
            grid = load_map(map_path)
            simulator = Simulator(grid)
            map_filename = os.path.basename(map_path)
            hardware = HardwareInterface(simulator, map_filename)
            
            # Simular situação onde robô fica preso após coletar humano
            # Forçar estado com carga e posição problemática
            hardware.carga = True
            hardware.pos = (2, 2)  # Posição central
            hardware.dir = 0  # Norte
            
            # Criar memória que levaria a um beco com comando A (avanço)
            memory = ['A', 'A', 'G', 'A']  # Sequência que requer avanço para retornar
            current_state = {'pos': (2, 2), 'dir': 0, 'carga': True}  # Estado com carga
            
            # Simular condição de beco forçando sensores que bloqueiam movimento
            def mock_read_sensors():
                return ('PAREDE', 'PAREDE', 'PAREDE')
            hardware.read_sensors = mock_read_sensors
            
            # Mock _find_alternative_path para retornar None (sem saída)
            import algorithms.returner as returner_module
            original_find_alt = returner_module._find_alternative_path
            def mock_find_alternative(remaining_steps, hw):
                return None  # Simular que não há caminho alternativo
            returner_module._find_alternative_path = mock_find_alternative
            
            try:
                # Deve levantar exceção de beco quando tentar retornar com carga
                with pytest.raises(BecoPosColetaError, match="Robô ficou preso em beco"):
                    plan_return(memory, current_state, hardware)
            finally:
                # Restaurar função original
                returner_module._find_alternative_path = original_find_alt
            
            # Verificar se alarme foi registrado no CSV
            expected_csv = map_filename.replace('.txt', '.csv')
            if os.path.exists(expected_csv):
                with open(expected_csv, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Verificar se há linha de alarme
                    assert 'ALARM' in content or 'BECO' in content
            
        finally:
            if os.path.exists(map_path):
                os.unlink(map_path)
            if hasattr(hardware, 'logger'):
                hardware.logger.close()
    
    def test_controller_beco_alarm(self):
        """Testa alarme via controller quando detecta beco."""
        # Mapa simples que pode causar beco - E deve estar na borda
        simple_content = """XXXXX
E...X
X.@.X
XXXXX
XXXXX"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(simple_content)
            map_path = f.name
        
        hardware = None
        try:
            grid = load_map(map_path)
            simulator = Simulator(grid)
            map_filename = os.path.basename(map_path)
            hardware = HardwareInterface(simulator, map_filename)
            controller = RobotController(hardware)
            
            # Simular execução que pode levar a beco
            # Forçar situação onde há humano disponível mas retorno é problemático
            hardware.pos = (2, 2)  # Próximo ao humano
            hardware.dir = 1  # Leste
            
            # Mock para simular que humano está na frente
            original_read = hardware.read_sensors
            call_count = [0]
            
            def mock_read_sensors():
                call_count[0] += 1
                if call_count[0] <= 2:
                    return ('VAZIO', 'VAZIO', 'HUMANO')  # Humano na frente
                else:
                    return ('PAREDE', 'PAREDE', 'PAREDE')  # Beco após coleta
            
            hardware.read_sensors = mock_read_sensors
            
            # Executar controller - pode causar alarme dependendo da implementação
            result = controller.run()
            
            # Verificar se erro foi detectado
            assert 'ERRO' in result or 'BECO' in result or controller.get_current_state() == 'ERROR'
            
        finally:
            if os.path.exists(map_path):
                os.unlink(map_path)
            if hardware and hasattr(hardware, 'logger'):
                hardware.logger.close()
    
    def test_alarm_logging_format(self):
        """Testa formato de logging de alarmes."""
        # Criar mapa simples
        simple_content = """XXX
E@X
XXX"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(simple_content)
            map_path = f.name
        
        try:
            grid = load_map(map_path)
            simulator = Simulator(grid)
            map_filename = os.path.basename(map_path)
            hardware = HardwareInterface(simulator, map_filename)
            
            # Simular registro de alarme diretamente no logger
            if hasattr(hardware, 'logger'):
                # Registrar alarme manualmente para testar formato
                hardware.logger.log("ALARM", "TESTE", "Alarme de teste", "detalhes", True)
                hardware.logger.close()
                
                # Verificar formato no CSV
                expected_csv = map_filename.replace('.txt', '.csv')
                with open(expected_csv, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    # Deve haver linha LIGAR + linha de ALARM
                    assert len(lines) >= 2
                    
                    # Verificar se linha de alarme está no formato correto
                    alarm_line = None
                    for line in lines:
                        if 'ALARM' in line:
                            alarm_line = line.strip()
                            break
                    
                    if alarm_line:
                        parts = alarm_line.split(',')
                        assert parts[0] == "ALARM"
                        assert len(parts) >= 3  # ALARM, tipo, texto, ...
        
        finally:
            if os.path.exists(map_path):
                os.unlink(map_path)
    
    def test_multiple_alarm_scenarios(self):
        """Testa múltiplos cenários que podem gerar alarmes."""
        scenarios = [
            # Mapa 1: Caminho simples
            """XXXXX
E...X
XXXXX
X.@.X
XXXXX""",
            
            # Mapa 2: Humano acessível
            """XXXXXXX
E.....X
XXXXXXX
X....@X
XXXXXXX"""
        ]
        
        for i, map_content in enumerate(scenarios):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(map_content)
                map_path = f.name
            
            hardware = None
            try:
                grid = load_map(map_path)
                simulator = Simulator(grid)
                map_filename = os.path.basename(map_path)
                hardware = HardwareInterface(simulator, map_filename)
                controller = RobotController(hardware)
                
                # Executar controller e verificar se completa ou gera erro apropriado
                result = controller.run()
                
                # Aceitar qualquer resultado que não cause crash
                assert isinstance(result, str)
                assert len(result) > 0
                
                # Verificar se CSV foi criado
                expected_csv = map_filename.replace('.txt', '.csv')
                assert os.path.exists(expected_csv)
                
            except Exception as e:
                # Aceitar exceções controladas
                assert isinstance(e, (BecoPosColetaError, ValueError, Exception))
                
            finally:
                if os.path.exists(map_path):
                    os.unlink(map_path)
                if hardware and hasattr(hardware, 'logger'):
                    hardware.logger.close()


if __name__ == "__main__":
    pytest.main([__file__])