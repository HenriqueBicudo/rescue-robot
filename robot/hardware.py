"""Responsável por interfacear com o hardware do robô."""

from typing import Tuple
from simulator.simulator import Simulator, RobotState
from .logger import Logger

__all__ = ['HardwareInterface']


class HardwareInterface:
    """Interface para comunicação com o hardware do robô."""
    
    def __init__(self, simulator: Simulator, map_filename: str):
        """
        Inicializa a interface de hardware.
        
        Args:
            simulator: Instância do simulador
            map_filename: Nome do arquivo de mapa
        """
        self.simulator = simulator
        
        # Localizar entrada via simulator
        entry_x, entry_y = self.simulator.find_entry()
        self.pos = (entry_x, entry_y)
        
        # Determinar direção inicial baseada na posição da entrada
        grid_height = self.simulator.height
        grid_width = self.simulator.width
        
        if entry_y == 0:  # Borda superior
            self.dir = 2  # Sul (S)
        elif entry_y == grid_height - 1:  # Borda inferior
            self.dir = 0  # Norte (N)
        elif entry_x == 0:  # Borda esquerda
            self.dir = 1  # Leste (E)
        elif entry_x == grid_width - 1:  # Borda direita
            self.dir = 3  # Oeste (W)
        else:
            # Não deveria acontecer se a validação do mapa estiver correta
            raise ValueError("Entrada não está na borda do mapa")
        
        # Inicializar estado interno
        self.carga = False
        
        # Criar logger e registrar linha LIGAR
        self.logger = Logger(map_filename)
        
        # Obter leituras iniciais dos sensores
        left, right, front = self.read_sensors()
        
        # Registrar linha LIGAR
        self.logger.log("LIGAR", left, right, front, self.carga)
    
    def read_sensors(self) -> Tuple[str, str, str]:
        """
        Lê dados dos sensores do robô.
        
        Returns:
            Tupla (left, right, front) com leituras dos sensores
        """
        return self.simulator.get_sensor_readings(self.pos, self.dir)
    
    def send_command(self, cmd: str) -> Tuple[str, str, str, bool]:
        """
        Envia comando para o robô e retorna estado atualizado.
        
        Args:
            cmd: Comando a ser executado (A, G, P, E)
            
        Returns:
            Tupla (left, right, front, carga_bool) após execução do comando
            
        Raises:
            CollisionError: Tentativa de mover para parede
            AtropelamentoError: Tentativa de mover para humano sem carga
            InvalidPickupError: Comando P inválido
            InvalidEjectError: Comando E inválido
        """
        # Criar estado atual
        current_state = RobotState(pos=self.pos, dir=self.dir, carga=self.carga)
        
        try:
            # Aplicar comando via simulator
            result = self.simulator.apply_command(current_state, cmd)
            
            # Atualizar estado interno
            self.pos = result.state.pos
            self.dir = result.state.dir
            self.carga = result.state.carga
            
            # Obter leituras após execução
            left, right, front = self.read_sensors()
            
            # Registrar linha no logger
            self.logger.log(cmd, left, right, front, self.carga)
            
            return (left, right, front, self.carga)
            
        except Exception as e:
            # Repropagar exceções do simulator sem escrever linha no log
            raise e
    
    def close(self) -> None:
        """Fecha recursos da interface."""
        if hasattr(self, 'logger'):
            self.logger.close()
    
    def __del__(self):
        """Destrutor para garantir fechamento de recursos."""
        self.close()