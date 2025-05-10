from reversible_circuit import ReversibleCircuit
from custom_types import Mapping
from bitarray.util import ba2hex
from custom_gate import CustomGate
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

# c_working = ReversibleCircuit(88, [
#     l_counter_gate(0, list(range(88))),
#     sbox_layer(list(range(88))),
#     l_counter_gate(1, get_permutation(list(range(88)))[0]),
#     sbox_layer(get_permutation(list(range(88)))[0]),
#     l_counter_gate(2, get_permutation(get_permutation(list(range(88)))[1])[0]),
# ])
# working_mapping = get_permutation(get_permutation(list(range(88)))[1])[1]

def pi_permutation_gate(gate_mapping: Mapping, register_mapping):
    pi_permutation = ReversibleCircuit(88)

    for round_number in range(45):
        pi_permutation.append_gate(l_counter_gate(round_number, gate_mapping))
        pi_permutation.append_gate(sbox_layer(gate_mapping))
        gate_mapping, register_mapping = get_permutation(register_mapping)
    
    return pi_permutation.to_gate(list(range(88)), "pi_permutation"), gate_mapping, register_mapping

c = ReversibleCircuit(88)
pi, gate_mapping, register_mapping = pi_permutation_gate(list(range(88)), list(range(88)))

c.append_gate(pi)

pi2, gate_mapping, register_mapping = pi_permutation_gate(gate_mapping, register_mapping)

c.append_gate(pi2)

pi3, gate_mapping, register_mapping = pi_permutation_gate(gate_mapping, register_mapping)

c.append_gate(pi3)

input_bits = "0"*88

result = c.run(input_bits)
# working_result = c_working.run(input_bits)

output = [None]*88
for position, bit in zip(reversed(register_mapping), result):
    output[87 - position] = bit

print(ba2hex(result))
print(ba2hex(bitarray(''.join(map(str, output)))))
