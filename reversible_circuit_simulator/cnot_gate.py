from reversible_gate import ReversibleGate
from custom_types import Mapping, Registers

class CNotGate(ReversibleGate):
    
    def __init__(self, gate_mapping: Mapping):
        super().__init__(gate_mapping=gate_mapping, input_count=2)

    def apply(self, registers: Registers):
        control_bit = len(registers) - 1 - self.gate_mapping[0]
        target_bit = len(registers) - 1 - self.gate_mapping[1]
        
        if registers[control_bit] == 1:
            new_registers = registers.copy()
            new_registers[target_bit] ^= 1
            return new_registers
        return registers
