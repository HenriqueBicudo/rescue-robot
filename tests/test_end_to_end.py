"""Testes end-to-end básicos do sistema."""

"""Testes end-to-end básicos do sistema."""

def test_all_imports():
    """Testa importação de todos os módulos do sistema."""
    try:
        # Simulator
        from simulator.map_loader import load_map
        from simulator.simulator import Simulator, RobotState, CollisionError, AtropelamentoError
        
        # Robot
        from robot.hardware import HardwareInterface
        from robot.logger import Logger
        
        # Controller
        from controller.controller import RobotController
        
        # Algorithms
        from algorithms.explorer import Explorer
        from algorithms.returner import Returner, BecoPosColetaError, plan_return
        
        assert True, "Todos os módulos e classes importados com sucesso"
    except ImportError as e:
        assert False, f"Erro na importação end-to-end: {e}"


def test_class_existence():
    """Verifica se todas as classes principais existem."""
    try:
        from simulator.map_loader import load_map
        from simulator.simulator import Simulator
        from robot.hardware import HardwareInterface
        from robot.logger import Logger
        from controller.controller import RobotController
        from algorithms.explorer import Explorer
        from algorithms.returner import Returner
        
        # Verificar se são callable/classes
        callables = [load_map, Simulator, HardwareInterface, Logger, 
                    RobotController, Explorer, Returner]
        
        for callable_obj in callables:
            assert callable(callable_obj), f"Objeto {callable_obj.__name__} não é callable"
        
        assert True, "Todas as classes principais existem e são válidas"
    except Exception as e:
        assert False, f"Erro na verificação de classes: {e}"


def test_map_files_exist():
    """Verifica se os arquivos de mapa existem."""
    import os
    
    maps_dir = "maps"
    expected_maps = ["map1.txt", "map2.txt", "map3.txt"]
    
    try:
        for map_file in expected_maps:
            map_path = os.path.join(maps_dir, map_file)
            assert os.path.exists(map_path), f"Arquivo {map_file} não encontrado"
        
        assert True, "Todos os arquivos de mapa existem"
    except Exception as e:
        assert False, f"Erro na verificação dos mapas: {e}"


if __name__ == "__main__":
    test_all_imports()
    test_class_existence()
    test_map_files_exist()
    print("Todos os testes end-to-end passaram!")