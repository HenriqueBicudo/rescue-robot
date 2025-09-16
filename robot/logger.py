"""Responsável por registrar logs das operações do robô."""

import os
from typing import Optional

__all__ = ['Logger']


class Logger:
    """Sistema de logging para o robô em formato CSV."""
    
    def __init__(self, map_filename: str):
        """
        Inicializa o sistema de logging.
        
        Args:
            map_filename: Nome do arquivo de mapa (com ou sem extensão .txt)
        """
        # Remove extensão .txt se presente
        if map_filename.endswith('.txt'):
            base_name = map_filename[:-4]
        else:
            base_name = map_filename
        
        self.csv_filename = f"{base_name}.csv"
        
        # Abre arquivo CSV para escrita
        self.file = open(self.csv_filename, 'w', encoding='utf-8')
    
    def log(self, command: str, left: str, right: str, front: str, carga_bool: bool) -> None:
        """
        Registra uma linha no log CSV.
        
        Args:
            command: Comando executado (LIGAR, A, G, P, E)
            left: Leitura do sensor esquerdo
            right: Leitura do sensor direito  
            front: Leitura do sensor frontal
            carga_bool: Se o robô tem carga (True=COM HUMANO, False=SEM CARGA)
        """
        # Converter carga para string literal
        carga_str = "COM HUMANO" if carga_bool else "SEM CARGA"
        
        # Escrever linha CSV
        line = f"{command},{left},{right},{front},{carga_str}\n"
        self.file.write(line)
        
        # Flush imediato
        self.file.flush()
    
    def close(self) -> None:
        """Fecha o arquivo de log."""
        if hasattr(self, 'file') and self.file:
            self.file.close()
    
    def __del__(self):
        """Destrutor para garantir fechamento do arquivo."""
        self.close()