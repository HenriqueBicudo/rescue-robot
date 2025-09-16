"""Testes pytest para os módulos simulator."""

import pytest
import tempfile
import os
from simulator.map_loader import load_map
from simulator.simulator import (
    Simulator, RobotState, CollisionError, AtropelamentoError, 
    InvalidPickupError, InvalidEjectError
)


class TestMapLoader:
    """Testes para o map_loader."""
    
    def test_load_map_valid(self):
        """Testa carregamento de mapa válido."""
        content = "XXXXX\nX...X\nX.@.X\nX...X\nEXXXX"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            grid = load_map(temp_path)
            assert len(grid) == 5
            assert len(grid[0]) == 5
            assert grid[4][0] == 'E'
            assert grid[2][2] == '@'
        finally:
            os.unlink(temp_path)
    
    def test_load_map_multiple_e(self):
        """Testa validação de múltiplas E."""
        content = "EXXXE\nX...X\nX.@.X\nX...X\nXXXXX"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Deve haver exatamente 1 'E', encontrado 2"):
                load_map(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_map_multiple_at(self):
        """Testa validação de múltiplos @."""
        content = "XXXXX\nX@..X\nX.@.X\nX...X\nEXXXX"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Deve haver exatamente 1 '@', encontrado 2"):
                load_map(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_map_e_not_on_border(self):
        """Testa validação de E não estar na borda."""
        content = "XXXXX\nX...X\nX.E.X\nX.@.X\nXXXXX"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="'E' deve estar na borda"):
                load_map(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_map_invalid_character(self):
        """Testa validação de caractere inválido."""
        content = "XXXXX\nX...X\nX.#.X\nX.@.X\nEXXXX"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Caractere inválido '#'"):
                load_map(temp_path)
        finally:
            os.unlink(temp_path)


class TestSimulator:
    """Testes para o Simulator."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Grid de teste padrão
        self.grid = [
            ['X', 'X', 'X', 'X', 'X'],
            ['X', '.', '.', '.', 'X'],
            ['X', '.', '@', '.', 'X'],
            ['X', '.', '.', '.', 'X'],
            ['E', 'X', 'X', 'X', 'X']
        ]
        self.simulator = Simulator(self.grid)
    
    def test_find_entry(self):
        """Testa localização da entrada."""
        entry = self.simulator.find_entry()
        assert entry == (0, 4)
    
    def test_get_sensor_readings_with_wall(self):
        """Testa leitura de sensores com parede."""
        # Posição (1, 1), direção Norte (0)
        readings = self.simulator.get_sensor_readings((1, 1), 0)
        left, right, front = readings
        
        # Esquerda: (0, 1) = 'X' -> PAREDE
        # Direita: (2, 1) = '.' -> VAZIO  
        # Frente: (1, 0) = 'X' -> PAREDE
        assert left == 'PAREDE'
        assert right == 'VAZIO'
        assert front == 'PAREDE'
    
    def test_get_sensor_readings_with_human(self):
        """Testa leitura de sensores com humano."""
        # Posição (1, 2), direção Leste (1)
        readings = self.simulator.get_sensor_readings((1, 2), 1)
        left, right, front = readings
        
        # Esquerda: (1, 1) = '.' -> VAZIO
        # Direita: (1, 3) = '.' -> VAZIO
        # Frente: (2, 2) = '@' -> HUMANO
        assert left == 'VAZIO'
        assert right == 'VAZIO'
        assert front == 'HUMANO'
    
    def test_get_sensor_readings_with_border(self):
        """Testa leitura de sensores na borda."""
        # Posição (0, 4), direção Oeste (3) - na entrada
        readings = self.simulator.get_sensor_readings((0, 4), 3)
        left, right, front = readings
        
        # Esquerda: (0, 5) = fora do grid -> VAZIO
        # Direita: (0, 3) = 'X' -> PAREDE
        # Frente: (-1, 4) = fora do grid -> VAZIO
        assert left == 'VAZIO'
        assert right == 'PAREDE'
        assert front == 'VAZIO'
    
    def test_apply_command_collision_error(self):
        """Testa CollisionError ao tentar mover para parede."""
        state = RobotState(pos=(1, 1), dir=0, carga=False)  # Norte
        
        with pytest.raises(CollisionError, match="Tentativa de mover para parede"):
            self.simulator.apply_command(state, 'A')
    
    def test_apply_command_atropelamento_error(self):
        """Testa AtropelamentoError ao tentar atropelar humano sem carga."""
        state = RobotState(pos=(1, 2), dir=1, carga=False)  # Leste, sem carga
        
        with pytest.raises(AtropelamentoError, match="Tentativa de atropelar humano sem carga"):
            self.simulator.apply_command(state, 'A')
    
    def test_apply_command_invalid_pickup_error(self):
        """Testa InvalidPickupError quando não há humano na frente."""
        state = RobotState(pos=(1, 1), dir=1, carga=False)  # Leste, célula vazia na frente
        
        with pytest.raises(InvalidPickupError, match="Não há humano na frente para pegar"):
            self.simulator.apply_command(state, 'P')
    
    def test_apply_command_pickup_success(self):
        """Testa comando P bem-sucedido."""
        state = RobotState(pos=(1, 2), dir=1, carga=False)  # Leste, humano na frente
        
        result = self.simulator.apply_command(state, 'P')
        
        # Estado deve ter carga True
        assert result.state.carga == True
        assert result.state.pos == (1, 2)  # Posição não muda
        assert result.state.dir == 1  # Direção não muda
        
        # Grid deve ter '.' onde estava '@'
        assert result.grid[2][2] == '.'
    
    def test_apply_command_move_forward(self):
        """Testa movimento para frente em célula vazia."""
        state = RobotState(pos=(1, 1), dir=1, carga=False)  # Leste
        
        result = self.simulator.apply_command(state, 'A')
        
        # Posição deve mudar para (2, 1)
        assert result.state.pos == (2, 1)
        assert result.state.dir == 1
        assert result.state.carga == False
    
    def test_apply_command_turn_right(self):
        """Testa rotação à direita."""
        state = RobotState(pos=(1, 1), dir=0, carga=False)  # Norte
        
        result = self.simulator.apply_command(state, 'G')
        
        # Direção deve mudar para Leste (1)
        assert result.state.dir == 1
        assert result.state.pos == (1, 1)  # Posição não muda
        assert result.state.carga == False
    
    def test_apply_command_move_with_cargo_over_human(self):
        """Testa movimento sobre humano quando já tem carga."""
        state = RobotState(pos=(1, 2), dir=1, carga=True)  # Leste, com carga
        
        result = self.simulator.apply_command(state, 'A')
        
        # Deve conseguir mover sobre o humano
        assert result.state.pos == (2, 2)
        assert result.state.carga == True
    
    def test_apply_command_invalid_eject_no_cargo(self):
        """Testa InvalidEjectError quando não tem carga."""
        state = RobotState(pos=(0, 4), dir=3, carga=False)  # Na entrada, sem carga
        
        with pytest.raises(InvalidEjectError, match="Robô não possui carga para ejetar"):
            self.simulator.apply_command(state, 'E')
    
    def test_apply_command_invalid_eject_not_at_entry(self):
        """Testa InvalidEjectError quando não está na entrada."""
        state = RobotState(pos=(1, 1), dir=3, carga=True)  # Não na entrada, com carga
        
        with pytest.raises(InvalidEjectError, match="Robô deve estar na entrada para ejetar"):
            self.simulator.apply_command(state, 'E')
    
    def test_apply_command_eject_success(self):
        """Testa comando E bem-sucedido."""
        state = RobotState(pos=(0, 4), dir=3, carga=True)  # Na entrada, direção Oeste, com carga
        
        result = self.simulator.apply_command(state, 'E')
        
        # Carga deve ser False
        assert result.state.carga == False
        assert result.state.pos == (0, 4)  # Posição não muda
        assert result.state.dir == 3  # Direção não muda


if __name__ == "__main__":
    pytest.main([__file__])