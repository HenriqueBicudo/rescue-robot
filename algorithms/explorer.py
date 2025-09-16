"""Responsável por implementar algoritmos de exploração do ambiente."""

from typing import List, Tuple, Set, Optional
from robot.hardware import HardwareInterface, SensorData

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
        raise NotImplementedError
    
    def explore_step(self) -> bool:
        """Executa um passo da exploração."""
        raise NotImplementedError
    
    def is_exploration_complete(self) -> bool:
        """Verifica se a exploração foi completada."""
        raise NotImplementedError
    
    def get_explored_area(self) -> Set[Tuple[int, int]]:
        """Retorna as áreas já exploradas."""
        raise NotImplementedError
    
    def find_victims(self) -> List[Tuple[int, int]]:
        """Retorna posições das vítimas encontradas."""
        raise NotImplementedError