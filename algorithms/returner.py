"""Responsável por implementar algoritmos de retorno à origem."""

from typing import List, Dict, Any
from robot.hardware import HardwareInterface

__all__ = ['Returner', 'BecoPosColetaError', 'plan_return']


class BecoPosColetaError(Exception):
    """Erro quando robô fica preso em beco após coletar humano."""
    pass


def plan_return(memory: List[str], current_state: Dict[str, Any], hardware: HardwareInterface) -> List[str]:
    """
    Planeja retorno à origem usando memória de passos.
    
    Args:
        memory: Pilha de comandos executados para chegar à posição atual
        current_state: Estado atual do robô (pos, dir, carga)
        hardware: Interface de hardware para leitura de sensores
        
    Returns:
        Lista de comandos para retornar à origem
        
    Raises:
        BecoPosColetaError: Quando robô fica preso em beco com carga
    """
    if not current_state.get('carga', False):
        # Se não tem carga, apenas inverte os comandos
        return _invert_commands(memory)
    
    # Com carga, precisa verificar segurança antes de cada movimento
    return_commands = []
    remaining_steps = _invert_commands(memory)
    
    for i, command in enumerate(remaining_steps):
        if command == 'A':  # Antes de avançar, verificar sensores
            left, right, front = hardware.read_sensors()
            
            if left == 'PAREDE' and right == 'PAREDE' and front == 'PAREDE':
                # Está em beco, tentar encontrar caminho alternativo
                alternative_path = _find_alternative_path(remaining_steps[i:], hardware)
                if alternative_path is None:
                    # Registrar alarme no logger se possível
                    if hasattr(hardware, 'logger'):
                        hardware.logger.log("ALARM", "BECO_POS_COLETA", "Robô preso em beco", "após coleta", True)
                    raise BecoPosColetaError("Robô ficou preso em beco após coletar humano")
                
                # Usar caminho alternativo
                return_commands.extend(alternative_path)
                break
        
        return_commands.append(command)
    
    return return_commands


def _invert_commands(commands: List[str]) -> List[str]:
    """
    Inverte uma sequência de comandos para retornar.
    
    Args:
        commands: Lista de comandos originais
        
    Returns:
        Lista de comandos invertidos
    """
    inverted = []
    
    # Processar comandos na ordem reversa
    for command in reversed(commands):
        if command == 'A':
            # Para desfazer um avanço, precisa girar 180° e avançar
            inverted.extend(['G', 'G', 'A', 'G', 'G'])
        elif command == 'G':
            # Para desfazer uma rotação à direita, fazer 3 rotações à direita (= 1 à esquerda)
            inverted.extend(['G', 'G', 'G'])
        # P e E não precisam ser desfeitos no retorno
    
    return inverted


def _find_alternative_path(remaining_steps: List[str], hardware: HardwareInterface) -> List[str]:
    """
    Tenta encontrar caminho alternativo quando detecta beco.
    
    Args:
        remaining_steps: Passos restantes do plano original
        hardware: Interface de hardware
        
    Returns:
        Lista de comandos alternativos ou None se não encontrar
    """
    # Implementação simplificada: tenta girar e encontrar saída
    alternatives = []
    
    # Tentar girar para diferentes direções
    for rotations in [1, 2, 3]:  # 90°, 180°, 270°
        test_commands = ['G'] * rotations
        
        # Simular rotação e verificar se há saída
        # Por simplicidade, assume que sempre há uma saída após rotação
        # Em implementação real, seria necessário simular movimento
        alternatives.append(test_commands + ['A'])
    
    # Retorna primeira alternativa (implementação simplificada)
    if alternatives:
        return alternatives[0]
    
    return None


class Returner:
    """Algoritmo de retorno à posição inicial."""
    
    def __init__(self, hardware: HardwareInterface):
        """Inicializa o algoritmo de retorno."""
        self.hardware = hardware
        self.memory = []  # Pilha de comandos executados
    
    def add_command_to_memory(self, command: str) -> None:
        """Adiciona comando à memória."""
        self.memory.append(command)
    
    def execute_return(self, current_state: Dict[str, Any]) -> List[str]:
        """
        Executa retorno à origem.
        
        Args:
            current_state: Estado atual do robô
            
        Returns:
            Lista de comandos executados no retorno
        """
        return_commands = plan_return(self.memory, current_state, self.hardware)
        
        # Executar comandos de retorno
        executed = []
        for command in return_commands:
            try:
                self.hardware.send_command(command)
                executed.append(command)
            except Exception as e:
                # Se falhar, registrar erro e parar
                if hasattr(self.hardware, 'logger'):
                    self.hardware.logger.log("ALARM", "ERRO_RETORNO", str(e), "", True)
                break
        
        return executed