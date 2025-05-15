from reversible_circuit import ReversibleCircuit
from custom_types import Mapping
from bitarray.util import ba2hex
from bitarray import bitarray

def lfsr_state(round: int, initial_state: str = '000101', taps: list = [4, 5]):
    """Default values are for SPONGENT-88"""
    state = list(map(int, initial_state))
    
    for _ in range(round):
        feedback_bit = 0
        for tap in taps:
            feedback_bit ^= state[len(initial_state) - 1 - tap]
        
        state =  state[1:] + [feedback_bit]
    
    return ''.join(map(str, state))

def l_counter_gate(round: int, gate_mapping: Mapping):
    state = lfsr_state(round)
    
    l_counter = ReversibleCircuit(88)

    for bit, i in enumerate(state[::-1]):
        if i == '1':
            l_counter.x(bit)
            l_counter.x(88 - 1 - bit)

    return l_counter.to_gate(gate_mapping, "lcounter")

def sbox_gate(gate_mapping: Mapping):
    sbox = ReversibleCircuit(4)

    sbox.x(1)
    sbox.ccx(2,1,0)
    sbox.cx(1,2)
    sbox.cx(3,0)
    sbox.cx(0,1)
    sbox.x(0)
    sbox.ccx(3,2,1)
    sbox.ccx(1,0,3)
    sbox.x(1)
    sbox.cx(2,0)             
    sbox.ccx(3,1,2)          
    sbox.cx(2,1)             
    sbox.cx(0,3)

    return sbox.to_gate(gate_mapping, "sbox")

def sbox_layer(gate_mapping: Mapping):
    sbox_layer = ReversibleCircuit(88)
    
    for i in range(0, 88, 4):
        sbox_layer.append_gate(sbox_gate(list(range(i, i + 4))))
    
    return sbox_layer.to_gate(gate_mapping, name="sbox_layer")

def get_permuted_index(index: int):
    assert 0 <= index < 88

    if 0 <= index <= 88 - 2:
        return int((index * 88 / 4) % (88 - 1))
    else:
        return index
    
def get_permutation(mapping: Mapping):
    new_mapping = [None]*88
    for i, j in enumerate(mapping):
        new_mapping[get_permuted_index(j)] = i
    reverse_mapping = [get_permuted_index(i) for i in mapping]
    return new_mapping, reverse_mapping

def pi_permutation_gate(gate_mapping: Mapping, register_mapping: Mapping):
    pi_permutation = ReversibleCircuit(88)

    for round_number in range(45):
        pi_permutation.append_gate(l_counter_gate(round_number, gate_mapping))
        pi_permutation.append_gate(sbox_layer(gate_mapping))
        gate_mapping, register_mapping = get_permutation(register_mapping)
    
    return pi_permutation.to_gate(list(range(88)), "pi_permutation"), gate_mapping, register_mapping

def absorb_phase_gate(message_size: int):
    padding_size = 8 - message_size % 8

    absorb_phase = ReversibleCircuit(88 + message_size - 8) # The first 8 bits of the message are fed directly into the first 8 bits of the state

    gate_mapping = list(range(88))
    register_mapping = list(range(88))

    remaining_bits = message_size - 8

    for i in range (0, message_size - 8, 8):
        pi_permutation, gate_mapping, register_mapping = pi_permutation_gate(gate_mapping, register_mapping)
        absorb_phase.append_gate(pi_permutation)

        for j, k in enumerate(range(i, i + min(8, remaining_bits))):
            absorb_phase.cx(88 + k, gate_mapping[j])

        remaining_bits -= min(8, remaining_bits)
        
        if remaining_bits == 0:

            if padding_size == 8:
                pi_permutation, gate_mapping, register_mapping = pi_permutation_gate(gate_mapping, register_mapping)
                absorb_phase.append_gate(pi_permutation)
            
            absorb_phase.x(gate_mapping[7])

            pi_permutation, gate_mapping, register_mapping = pi_permutation_gate(gate_mapping, register_mapping)
            absorb_phase.append_gate(pi_permutation)
                    
    return absorb_phase.to_gate(list(range(88 + message_size - 8)), "absorb_phase"), gate_mapping, register_mapping

def squeeze_phase_gate(message_size: int, gate_mapping: int, register_mapping: int):
    circuit_width = 88 + message_size - 8 + 88 # 88 bits for the state + (message_size - 8) bits for the message + 88 bits for the output hash

    squeeze_phase = ReversibleCircuit(circuit_width) 

    for i in range (0, message_size, 8):
        for j in range(8):
            squeeze_phase.cx(gate_mapping[j], circuit_width - 8 - i + j)
        pi_permutation, gate_mapping, register_mapping = pi_permutation_gate(gate_mapping, register_mapping)
        
        if i < message_size - 8: # Don't add a permutation gate at the end.
            squeeze_phase.append_gate(pi_permutation)
    
    return squeeze_phase.to_gate(list(range(88 + message_size - 8 + 88)), "squeeze_phase"), gate_mapping, register_mapping

message_size = 256

c = ReversibleCircuit(88 + message_size - 8 + 88)

absorb_gate, gate_mapping, register_mapping = absorb_phase_gate(message_size)
squeeze_gate, _, register_mapping = squeeze_phase_gate(message_size, gate_mapping, register_mapping)

c.append_gate(absorb_gate)
c.append_gate(squeeze_gate)

input_bits = "0"*88 + "0"*224 + "011000010111000001110101" + "0"*80 + "01100100"

result = c.run(input_bits)

state = [None]*88
for position, bit in zip(reversed(register_mapping), result[-88:]):
    state[87 - position] = bit

output = result[0:88]

print(ba2hex(result))
print(ba2hex(bitarray(''.join(map(str, state)))))
print(ba2hex(bitarray(''.join(map(str, output)))))
