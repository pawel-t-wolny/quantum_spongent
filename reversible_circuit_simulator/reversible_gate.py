from abc import ABC, abstractmethod
from custom_types import Mapping, Registers



class ReversibleGate(ABC):
    
    gate_mapping: Mapping

    #   Gate mapping determines mapping of gate inputs to the input registers.
    #   The drawing below shows how would the input bits be mapped when gate_mapping = [0,1,2].
    # 
    #         Inputs:    X3     X2     X1     X0
    #                     |      |      |      |
    #                     |      v      v      v
    #                     |    +-----------------+
    #                     |    | 2      1      0 |
    #                     |    |    3x3 Gate     |
    #                     |    |                 |
    #                     |    +-----------------+
    #                     |      |      |      |
    #         Outputs:   Y0     Y1     Y2     Y3
    #
    #   If gate_mapping = [3, 0, 1], the circuit will look as follows:
    #
    #         Inputs:    X3     X2     X1     X0
    #                     |      |      |      |
    #                     v      |      v      v
    #                 +--------------------------+
    #                 |   0             2      1 |
    #                 |      Custom 3x3 Gate     |
    #                 |                          |
    #                 +--------------------------+
    #                     |      |      |      |
    #         Outputs:   Y0     Y1     Y2     Y3
    #
    #   So for each entry of the array think like "The input 0 of the gate gets mapped to input register 3, 
    #   input 1 gets mapped to input register 0, etc.".
    #
    #   To make it even more clear here is an example with a CCNOT gate on 4 registers. When 
    #   gate_mapping = [0, 1, 2] we get:
    #   
    #         Inputs:    X3     X2     X1     X0
    #                     |      |      |      |
    #                     v      v      v      v
    #                     |      2      1      0
    #                     |      X------o------o
    #                     |      |      |      |
    #         Outputs:   Y0     Y1     Y2     Y3 
    #
    #   Let's say we want to remap the gate using gate_mapping = [3, 0, 1]. Then we get:
    #
    #         Inputs:    X3     X2     X1     X0
    #                     |      |      |      |
    #                     v      v      v      v
    #                     0      |      2      1
    #                     o-------------X------o
    #                     |      |      |      |
    #         Outputs:   Y0     Y1     Y2     Y3 
    #
    #   As we can see, the input 0 of the CNOT gate was mapped to input register X3, 
    #   input 1 of the CNOT gate to input register X0 and input 2 of the CNOT gate was
    #   mapped to input register X1.

    input_count: int

    def __init__(self, gate_mapping: Mapping, input_count: int):
        super().__init__()

        for i in gate_mapping:
            assert 0 <= i
        
        assert len(set(gate_mapping)) == len(gate_mapping)
        
        assert input_count == len(gate_mapping)

        self.gate_mapping = gate_mapping
        self.input_count = input_count



    @abstractmethod
    def apply(self, registers: Registers) -> Registers: ...
