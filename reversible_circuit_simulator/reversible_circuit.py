from reversible_gate import ReversibleGate
from custom_types import Mapping, Registers
from reversible_gate import Registers
from typing import List
from not_gate import NotGate
from cnot_gate import CNotGate
from ccnot_gate import CCNotGate
from bitarray import bitarray

class ReversibleCircuit:
    gates: List[ReversibleGate]
    width: int

    def __init__(self, width: int, gates: List[ReversibleGate] = None):
        if gates is None:
            gates = []

        for gate in gates:
            assert gate.input_count <= width

        self.gates = gates
        self.width = width

    def run(self, initial_values: str) -> Registers:
        assert len(initial_values) == self.width
        registers = bitarray(initial_values)
        for gate in self.gates:
            registers = gate.apply(registers)
        
        return registers
    
    def append_gate(self, gate: ReversibleGate):
        assert gate.input_count <= self.width

        for bit in gate.gate_mapping:
            assert bit < self.width

        self.gates.append(gate)

    def to_gate(self, gate_mapping: Mapping, name: str) -> ReversibleGate:
        from custom_gate import CustomGate
        return CustomGate(self, gate_mapping, name)

    def x(self, target_bit: int):
        gate = NotGate([target_bit])
        self.append_gate(gate)

    def cx(self, control_bit: int, target_bit: int):
        gate = NotGate([control_bit, target_bit])
        self.append_gate(gate)

    def cx(self, control_bit: int, target_bit: int):
        gate = CNotGate([control_bit, target_bit])
        self.append_gate(gate)

    def ccx(self, control_bit1: int, control_bit2:int, target_bit: int):
        gate = CCNotGate([control_bit1, control_bit2, target_bit])
        self.append_gate(gate)
