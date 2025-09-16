"""Testes end-to-end básicos do sistema."""

def test_all_imports():
    """Testa importação de todos os módulos do sistema."""
    try:
        # Simulator
        from simulator.map_loader import MapData, load_map, validate_map
        from simulator.simulator import Simulator, RobotState
        
        # Robot
        from robot.hardware import HardwareInterface, SensorData
        from robot.logger import RobotLogger, LogLevel
        
        # Controller
        from controller.controller import RobotController, ControllerState
        
        # Algorithms
        from algorithms.explorer import Explorer, ExplorationStrategy
        from algorithms.returner import Returner, PathPlanningStrategy
        
        assert True, "Todos os módulos e classes importados com sucesso"
    except ImportError as e:
        assert False, f"Erro na importação end-to-end: {e}"


def test_class_existence():
    """Verifica se todas as classes principais existem."""
    try:
        from simulator.map_loader import MapData
        from simulator.simulator import Simulator
        from robot.hardware import HardwareInterface
        from robot.logger import RobotLogger
        from controller.controller import RobotController
        from algorithms.explorer import Explorer
        from algorithms.returner import Returner
        
        classes = [MapData, Simulator, HardwareInterface, RobotLogger, 
                  RobotController, Explorer, Returner]
        
        for cls in classes:
            assert cls is not None, f"Classe {cls.__name__} não existe"
        
        assert True, "Todas as classes principais existem"
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