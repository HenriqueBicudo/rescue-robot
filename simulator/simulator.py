"""Responsável por simular o ambiente e a movimentação do robô."""

from typing import List, Tuple
from dataclasses import dataclass
import copy

__all__ = ['Simulator', 'RobotState', 'RobotStateResult', 'CollisionError', 'AtropelamentoError', 'InvalidPickupError', 'InvalidEjectError']


# Exceções
class CollisionError(Exception):
    """Erro de colisão com parede."""
    pass

class AtropelamentoError(Exception):
    """Erro de atropelamento de humano."""
    pass

class InvalidPickupError(Exception):
    """Erro de comando P inválido."""
    pass

class InvalidEjectError(Exception):
    """Erro de comando E inválido."""
    pass


@dataclass
class RobotState:
    """Representa o estado atual do robô na simulação."""
    pos: Tuple[int, int]  # (x, y)
    dir: int  # 0=N, 1=E, 2=S, 3=W
    carga: bool  # False=SEM CARGA, True=COM HUMANO


@dataclass
class RobotStateResult:
    """Resultado após aplicar um comando."""
    state: RobotState
    grid: List[List[str]]


class Simulator:
    """Simula o ambiente e controla a movimentação do robô."""
    
    def __init__(self, grid: List[List[str]]):
        """Inicializa o simulador com um grid."""
        self.original_grid = [row[:] for row in grid]  # Cópia profunda
        self.grid = [row[:] for row in grid]  # Grid de trabalho
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
    
    def find_entry(self) -> Tuple[int, int]:
        """Retorna posição (x, y) da entrada 'E'."""
        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                if char == 'E':
                    return (x, y)
        raise ValueError("Entrada 'E' não encontrada no grid")
    
    def _get_adjacent_pos(self, pos: Tuple[int, int], direction: int) -> Tuple[int, int]:
        """Retorna posição adjacente na direção especificada."""
        x, y = pos
        
        # 0=N, 1=E, 2=S, 3=W
        if direction == 0:  # Norte
            return (x, y - 1)
        elif direction == 1:  # Leste
            return (x + 1, y)
        elif direction == 2:  # Sul
            return (x, y + 1)
        elif direction == 3:  # Oeste
            return (x - 1, y)
        else:
            raise ValueError(f"Direção inválida: {direction}")
    
    def _is_position_valid(self, pos: Tuple[int, int]) -> bool:
        """Verifica se a posição está dentro do grid."""
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height
    
    def _get_cell_content(self, pos: Tuple[int, int]) -> str:
        """Retorna o conteúdo da célula ou 'VAZIO' se fora do grid."""
        if not self._is_position_valid(pos):
            return 'VAZIO'
        
        x, y = pos
        cell = self.grid[y][x]
        
        if cell == 'X':
            return 'PAREDE'
        elif cell == '@':
            return 'HUMANO'
        else:  # '.', 'E'
            return 'VAZIO'
    
    def get_sensor_readings(self, pos: Tuple[int, int], dir: int) -> Tuple[str, str, str]:
        """
        Retorna leituras dos sensores (left, right, front).
        
        Args:
            pos: Posição atual (x, y)
            dir: Direção atual (0=N, 1=E, 2=S, 3=W)
            
        Returns:
            Tupla (left, right, front) com valores 'PAREDE', 'VAZIO', 'HUMANO'
        """
        # Calcular direções relativas
        left_dir = (dir - 1) % 4
        right_dir = (dir + 1) % 4
        front_dir = dir
        
        # Obter posições adjacentes
        left_pos = self._get_adjacent_pos(pos, left_dir)
        right_pos = self._get_adjacent_pos(pos, right_dir)
        front_pos = self._get_adjacent_pos(pos, front_dir)
        
        # Obter conteúdo das células
        left_reading = self._get_cell_content(left_pos)
        right_reading = self._get_cell_content(right_pos)
        front_reading = self._get_cell_content(front_pos)
        
        return (left_reading, right_reading, front_reading)
    
    def apply_command(self, state: RobotState, command: str) -> RobotStateResult:
        """
        Aplica um comando ao robô e retorna o novo estado.
        
        Args:
            state: Estado atual do robô
            command: Comando ('A', 'G', 'P', 'E')
            
        Returns:
            RobotStateResult com novo estado e grid
            
        Raises:
            CollisionError: Tentativa de mover para parede
            AtropelamentoError: Tentativa de mover para humano sem carga
            InvalidPickupError: Comando P inválido
            InvalidEjectError: Comando E inválido
        """
        # Criar cópias para não modificar o estado original
        new_state = RobotState(pos=state.pos, dir=state.dir, carga=state.carga)
        new_grid = [row[:] for row in self.grid]
        
        if command == 'A':  # Avançar
            front_pos = self._get_adjacent_pos(state.pos, state.dir)
            
            if not self._is_position_valid(front_pos):
                # Fora do grid, pode mover
                new_state.pos = front_pos
            else:
                x, y = front_pos
                front_cell = self.grid[y][x]
                
                if front_cell == 'X':
                    raise CollisionError("Tentativa de mover para parede")
                elif front_cell == '@' and not state.carga:
                    raise AtropelamentoError("Tentativa de atropelar humano sem carga")
                else:
                    # Pode mover (célula vazia, E, ou @ com carga)
                    new_state.pos = front_pos
        
        elif command == 'G':  # Girar à direita
            new_state.dir = (state.dir + 1) % 4
        
        elif command == 'P':  # Pegar humano
            front_pos = self._get_adjacent_pos(state.pos, state.dir)
            
            if not self._is_position_valid(front_pos):
                raise InvalidPickupError("Não há humano na frente para pegar")
            
            x, y = front_pos
            front_cell = self.grid[y][x]
            
            if front_cell != '@':
                raise InvalidPickupError("Não há humano na frente para pegar")
            
            # Remover @ do grid e definir carga
            new_grid[y][x] = '.'
            new_state.carga = True
        
        elif command == 'E':  # Ejetar humano
            if not state.carga:
                raise InvalidEjectError("Robô não possui carga para ejetar")
            
            # Verificar se está na entrada
            entry_pos = self.find_entry()
            if state.pos != entry_pos:
                raise InvalidEjectError("Robô deve estar na entrada para ejetar")
            
            # Verificar se está de frente para a saída
            # A direção da frente deve levar para fora do grid
            front_pos = self._get_adjacent_pos(state.pos, state.dir)
            
            if self._is_position_valid(front_pos):
                raise InvalidEjectError("Robô não está de frente para a saída")
            
            new_state.carga = False
        
        else:
            raise ValueError(f"Comando inválido: {command}")
        
        # Atualizar o grid interno
        self.grid = new_grid
        
        return RobotStateResult(state=new_state, grid=new_grid)