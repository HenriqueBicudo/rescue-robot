"""Responsável por carregar e validar mapas de arquivos .txt."""

from typing import List

__all__ = ['load_map']


def load_map(path: str) -> List[List[str]]:
    """
    Lê arquivo .txt UTF-8 e retorna grid validado.
    
    Args:
        path: Caminho para o arquivo .txt
        
    Returns:
        Grid indexado por [y][x]
        
    Raises:
        ValueError: Se o mapa for inválido
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            lines = [line.rstrip('\n\r') for line in file.readlines()]
    except FileNotFoundError:
        raise ValueError(f"Arquivo não encontrado: {path}")
    except UnicodeDecodeError:
        raise ValueError(f"Erro de codificação UTF-8 no arquivo: {path}")
    
    if not lines:
        raise ValueError("Arquivo vazio")
    
    # Remove linhas vazias no final
    while lines and not lines[-1]:
        lines.pop()
        
    if not lines:
        raise ValueError("Arquivo não contém dados válidos")
    
    # Criar grid
    grid = []
    for line in lines:
        grid.append(list(line))
    
    # Validar caracteres permitidos
    valid_chars = {'X', '.', '@', 'E'}
    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            if char not in valid_chars:
                raise ValueError(f"Caractere inválido '{char}' na posição ({x}, {y})")
    
    # Verificar formato retangular
    if not grid:
        raise ValueError("Grid vazio")
        
    width = len(grid[0])
    for y, row in enumerate(grid):
        if len(row) != width:
            raise ValueError(f"Linha {y} tem comprimento {len(row)}, esperado {width}")
    
    # Contar E e @
    e_count = 0
    at_count = 0
    e_positions = []
    
    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            if char == 'E':
                e_count += 1
                e_positions.append((x, y))
            elif char == '@':
                at_count += 1
    
    # Validar exatamente 1 E e 1 @
    if e_count != 1:
        raise ValueError(f"Deve haver exatamente 1 'E', encontrado {e_count}")
    
    if at_count != 1:
        raise ValueError(f"Deve haver exatamente 1 '@', encontrado {at_count}")
    
    # Validar E na borda
    e_x, e_y = e_positions[0]
    height = len(grid)
    width = len(grid[0])
    
    is_on_border = (e_y == 0 or e_y == height - 1 or e_x == 0 or e_x == width - 1)
    
    if not is_on_border:
        raise ValueError(f"'E' deve estar na borda, encontrado na posição ({e_x}, {e_y})")
    
    return grid