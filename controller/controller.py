"""Responsável por controlar a execução dos algoritmos do robô."""

from typing import List, Dict, Any
from robot.hardware import HardwareInterface
from algorithms.returner import Returner, plan_return, BecoPosColetaError
from simulator.simulator import InvalidPickupError, CollisionError, AtropelamentoError

__all__ = ['RobotController', 'ControllerState']


class ControllerState:
    """Estados possíveis do controlador."""
    IDLE = "IDLE"
    EXPLORING = "EXPLORING"
    RETURNING = "RETURNING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class RobotController:
    """Controlador principal do robô."""
    
    def __init__(self, hardware: HardwareInterface):
        """Inicializa o controlador do robô."""
        self.hardware = hardware
        self.returner = Returner(hardware)
        self.state = ControllerState.IDLE
        self.memory = []  # Memória de comandos executados
        self.current_state = {
            'pos': hardware.pos,
            'dir': hardware.dir,
            'carga': hardware.carga
        }
    
    def run(self) -> str:
        """
        Executa missão completa do robô.
        
        Returns:
            Estado final da missão
        """
        try:
            self.state = ControllerState.EXPLORING
            
            # Fase de exploração simples - buscar humano
            human_found = self._explore_for_human()
            
            if human_found:
                # Executar comando P para pegar humano
                self._execute_command('P')
                
                # Iniciar retorno
                self.state = ControllerState.RETURNING
                self._execute_return()
                
                # Ejetar humano na saída
                self._execute_command('E')
                
                self.state = ControllerState.COMPLETED
                return "MISSAO_COMPLETADA"
            else:
                self.state = ControllerState.COMPLETED
                return "HUMANO_NAO_ENCONTRADO"
                
        except BecoPosColetaError as e:
            self.state = ControllerState.ERROR
            return f"BECO_POS_COLETA: {str(e)}"
        except Exception as e:
            self.state = ControllerState.ERROR
            return f"ERRO: {str(e)}"
    
    def _explore_for_human(self) -> bool:
        """
        Exploração simples para encontrar humano.
        
        Returns:
            True se humano foi encontrado e está acessível
        """
        max_steps = 50  # Limite para evitar loop infinito
        steps = 0
        
        while steps < max_steps:
            left, right, front = self.hardware.read_sensors()
            
            # Se há humano na frente, retorna True
            if front == 'HUMANO':
                return True
            
            # Estratégia simples: seguir parede à direita
            if right != 'PAREDE':
                # Girar à direita e avançar
                self._execute_command('G')
                if self._can_move_forward():
                    self._execute_command('A')
            elif front != 'PAREDE':
                # Avançar se possível
                self._execute_command('A')
            else:
                # Girar à esquerda (3 rotações à direita)
                self._execute_command('G')
                self._execute_command('G')
                self._execute_command('G')
            
            steps += 1
        
        return False
    
    def _can_move_forward(self) -> bool:
        """Verifica se pode mover para frente."""
        left, right, front = self.hardware.read_sensors()
        return front != 'PAREDE'
    
    def _execute_command(self, command: str) -> None:
        """
        Executa comando e atualiza estado.
        
        Args:
            command: Comando a ser executado
        """
        try:
            left, right, front, carga = self.hardware.send_command(command)
            
            # Atualizar estado interno
            self.current_state['pos'] = self.hardware.pos
            self.current_state['dir'] = self.hardware.dir
            self.current_state['carga'] = carga
            
            # Adicionar à memória (exceto comandos de retorno)
            if self.state == ControllerState.EXPLORING:
                self.memory.append(command)
                self.returner.add_command_to_memory(command)
            
        except Exception as e:
            # Repropagar exceção
            raise e
    
    def _execute_return(self) -> None:
        """Executa sequência de retorno à origem."""
        try:
            return_commands = plan_return(self.memory, self.current_state, self.hardware)
            
            for command in return_commands:
                left, right, front, carga = self.hardware.send_command(command)
                
                # Atualizar estado
                self.current_state['pos'] = self.hardware.pos
                self.current_state['dir'] = self.hardware.dir
                self.current_state['carga'] = carga
                
        except BecoPosColetaError:
            # Repropagar erro de beco
            raise
        except Exception as e:
            # Outros erros durante retorno
            raise Exception(f"Erro durante retorno: {str(e)}")
    
    def get_current_state(self) -> str:
        """Retorna o estado atual do controlador."""
        return self.state
    
    def get_memory(self) -> List[str]:
        """Retorna memória de comandos executados."""
        return self.memory.copy()