from reversible_gate import ReversibleGate
from custom_types import Mapping, Registers

class NotGate(ReversibleGate):
    
    def __init__(self, gate_mapping: Mapping):
        super().__init__(gate_mapping=gate_mapping, input_count=1)

    def apply(self, registers: Registers):
        new_registers = registers.copy()
        target_bit = len(registers) - 1 - self.gate_mapping[0]
        new_registers[target_bit] ^= 1

        return new_registers
