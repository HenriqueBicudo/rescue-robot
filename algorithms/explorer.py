"""Responsável por implementar algoritmos de exploração do ambiente."""

from typing import List, Tuple, Set, Optional
from robot.hardware import HardwareInterface

__all__ = ['Explorer', 'ExplorationStrategy']


class ExplorationStrategy:
    """Estratégias de exploração disponíveis."""
    DEPTH_FIRST = "DEPTH_FIRST"
    BREADTH_FIRST = "BREADTH_FIRST"
    WALL_FOLLOWING = "WALL_FOLLOWING"


class Explorer:
    """Algoritmo de exploração do ambiente."""
    
    def __init__(self, hardware: HardwareInterface, strategy: str = ExplorationStrategy.WALL_FOLLOWING):
        """Inicializa o explorador com uma estratégia."""
        self.hardware = hardware
        self.strategy = strategy
        self.explored_positions = set()
        self.found_victims = []
    
    def explore_step(self) -> bool:
        """Executa um passo da exploração."""
        # Implementação básica de wall-following
        left, right, front = self.hardware.read_sensors()
        
        # Marcar posição atual como explorada
        current_pos = (self.hardware.pos[0], self.hardware.pos[1])
        self.explored_positions.add(current_pos)
        
        # Detectar humanos
        if front == 'HUMANO':
            victim_pos = self._calculate_front_position()
            if victim_pos not in self.found_victims:
                self.found_victims.append(victim_pos)
        
        # Lógica simples de movimento (preferir esquerda > frente > direita)
        if left == 'VAZIO':
            self.hardware.send_command('G')  # Girar para a esquerda
            self.hardware.send_command('G')  
            self.hardware.send_command('G')
            self.hardware.send_command('A')  # Avançar
            return True
        elif front == 'VAZIO':
            self.hardware.send_command('A')  # Avançar
            return True
        elif right == 'VAZIO':
            self.hardware.send_command('G')  # Girar para a direita
            self.hardware.send_command('A')  # Avançar
            return True
        else:
            # Dar meia volta
            self.hardware.send_command('G')
            self.hardware.send_command('G')
            return True
    
    def _calculate_front_position(self) -> Tuple[int, int]:
        """Calcula posição na frente do robô baseado na direção atual."""
        x, y = self.hardware.pos
        direction = self.hardware.dir
        
        if direction == 0:  # Norte
            return (x, y - 1)
        elif direction == 1:  # Leste
            return (x + 1, y)
        elif direction == 2:  # Sul
            return (x, y + 1)
        elif direction == 3:  # Oeste
            return (x - 1, y)
        
        return (x, y)
    
    def is_exploration_complete(self) -> bool:
        """Verifica se a exploração foi completada."""
        # Critério simples: encontrou pelo menos um humano
        return len(self.found_victims) > 0
    
    def get_explored_area(self) -> Set[Tuple[int, int]]:
        """Retorna as áreas já exploradas."""
        return self.explored_positions.copy()
    
    def find_victims(self) -> List[Tuple[int, int]]:
        """Retorna posições das vítimas encontradas."""
        return self.found_victims.copy()