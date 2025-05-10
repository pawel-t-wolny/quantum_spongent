from reversible_gate import ReversibleGate
from custom_types import Mapping, Registers

class CCNotGate(ReversibleGate):
    
    def __init__(self, gate_mapping: Mapping):
        super().__init__(gate_mapping=gate_mapping, input_count=3)

    def apply(self, registers: Registers):
        first_control_bit = len(registers) - 1 - self.gate_mapping[0]
        second_control_bit = len(registers) - 1 - self.gate_mapping[1]
        target_bit = len(registers) - 1 - self.gate_mapping[2]
        
        if registers[first_control_bit] == 1 and registers[second_control_bit] == 1:
            new_registers = registers.copy()
            new_registers[target_bit] ^= 1
            return new_registers
        return registers