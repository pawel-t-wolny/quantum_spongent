from bitarray.util import ba2hex
from bitarray import bitarray
import sys

from revsim import *

# Specifications for SPONGENT-88

R = 8  # Rate
B = 88  # State width
N = 88  # Hash size
ROUNDS = 45  # Number of rounds in the Pi permutation
INITIAL_LFSR_STATE = "000101"
LFSR_TAPS = [4, 5]
SBOX_WIDTH = 4

def lfsr_state(
    round: int, initial_state: str = INITIAL_LFSR_STATE, taps: list = LFSR_TAPS
):
    state = list(map(int, initial_state))

    for _ in range(round):
        feedback_bit = 0
        for tap in taps:
            feedback_bit ^= state[len(initial_state) - 1 - tap]

        state = state[1:] + [feedback_bit]

    return "".join(map(str, state))


def l_counter_gate_factory(round: int):
    state = lfsr_state(round)

    l_counter = ReversibleCircuit(B)

    for bit, i in enumerate(state[::-1]):
        if i == "1":
            l_counter.x(bit)
            l_counter.x(B - 1 - bit)

    return l_counter.to_gate("lcounter")


def sbox_gate_factory():
    sbox = ReversibleCircuit(SBOX_WIDTH)

    sbox.x(1)
    sbox.ccx(2, 1, 0)
    sbox.cx(1, 2)
    sbox.cx(3, 0)
    sbox.cx(0, 1)
    sbox.x(0)
    sbox.ccx(3, 2, 1)
    sbox.ccx(1, 0, 3)
    sbox.x(1)
    sbox.cx(2, 0)
    sbox.ccx(3, 1, 2)
    sbox.cx(2, 1)
    sbox.cx(0, 3)

    return sbox.to_gate("sbox")


def sbox_layer_factory():
    sbox_layer = ReversibleCircuit(B)

    for i in range(0, B, SBOX_WIDTH):
        sbox_layer.append(sbox_gate_factory(), list(range(i, i + SBOX_WIDTH)))

    return sbox_layer.to_gate("sbox_layer")


def get_permuted_index(index: int):
    assert 0 <= index < B

    if 0 <= index <= B - 2:
        return int((index * B / 4) % (B - 1))
    else:
        return index


def get_permutation(mapping: Mapping):
    new_mapping = [None] * B
    for i, j in enumerate(mapping):
        new_mapping[get_permuted_index(j)] = i
    reverse_mapping = [get_permuted_index(i) for i in mapping]
    return new_mapping, reverse_mapping


def pi_permutation_gate(gate_mapping: Mapping, register_mapping: Mapping):
    pi_permutation = ReversibleCircuit(B)

    for round_number in range(ROUNDS):
        l_counter_gate = l_counter_gate_factory(round_number)
        sbox_layer_gate = sbox_layer_factory()

        pi_permutation.append(l_counter_gate, gate_mapping)
        pi_permutation.append(sbox_layer_gate, gate_mapping)
        gate_mapping, register_mapping = get_permutation(register_mapping)

    return pi_permutation.to_gate("pi_permutation"), gate_mapping, register_mapping


def absorb_phase_gate_factory(message_size: int):
    excess_bits = message_size % R
    padding_size = R - excess_bits

    absorb_phase = ReversibleCircuit(
        B + message_size - R
    )  # The first 8 bits of the message are fed directly into the first 8 bits of the state

    gate_mapping = list(range(B))
    register_mapping = list(range(B))

    remaining_bits = message_size - R

    for i in range(0, message_size - R - excess_bits, R):
        pi_permutation, gate_mapping, register_mapping = pi_permutation_gate(
            gate_mapping, register_mapping
        )
        absorb_phase.append(pi_permutation, list(range(B)))

        for j, k in enumerate(range(i, i + R)):
            absorb_phase.cx(B + k, gate_mapping[j])

        remaining_bits -= R

        if remaining_bits < R:
            pi_permutation, gate_mapping, register_mapping = pi_permutation_gate(
                gate_mapping, register_mapping
            )
            absorb_phase.append(pi_permutation, list(range(B)))

            i += R
            for n, m in enumerate(range(i, i + excess_bits)):
                absorb_phase.cx(B + m, gate_mapping[padding_size + n])
            absorb_phase.x(gate_mapping[padding_size - 1])

            pi_permutation, gate_mapping, register_mapping = pi_permutation_gate(
                gate_mapping, register_mapping
            )
            absorb_phase.append(pi_permutation, list(range(B)))

    return absorb_phase.to_gate("absorb_phase"), gate_mapping, register_mapping


def squeeze_phase_gate_factory(
    message_size: int, gate_mapping: int, register_mapping: int
):
    squeeze_phase = ReversibleCircuit(B + message_size - R + N)

    for i in range(0, N, R):
        for j in range(R):
            squeeze_phase.cx(gate_mapping[j], squeeze_phase.width - R - i + j)

        if i < B - R:  # Don't add a permutation gate at the end.
            pi_permutation, gate_mapping, register_mapping = pi_permutation_gate(
                gate_mapping, register_mapping
            )
            squeeze_phase.append(pi_permutation, list(range(B)))

    return squeeze_phase.to_gate("squeeze_phase"), gate_mapping, register_mapping


def reversible_spongent_gate_factory(message_size: int):
    spongent = ReversibleCircuit(B + message_size - R + N)

    absorb_gate, gate_mapping, register_mapping = absorb_phase_gate_factory(
        message_size
    )
    squeeze_gate, _, register_mapping = squeeze_phase_gate_factory(
        message_size, gate_mapping, register_mapping
    )

    spongent.append(absorb_gate, list(range(spongent.width - N)))
    spongent.append(squeeze_gate, list(range(spongent.width)))

    return spongent.to_gate("spongent"), register_mapping

def spongent_circuit(message_size: int):
    circuit_width = B + message_size - R + N
    spongent_circuit = ReversibleCircuit(circuit_width)
    spongent_gate, register_mapping = reversible_spongent_gate_factory(message_size)
    spongent_circuit.append(spongent_gate, list(range(circuit_width)))

    return spongent_circuit, register_mapping

quiet = False

match len(sys.argv):
    case 3:
        if sys.argv[1] == "-q":
            quiet = True
            message = sys.argv[2]
        else:
            print(f"Invalid flag: {sys.argv[1]}")
            exit(1)
    case 2:
        message = sys.argv[1]
    case 1:
        message = "Monkey"
    case _:
        print("Wrong number of arguments.")
        exit(1)

message_encoded = message.encode()

message_size = len(message) * 8
message_bytes = [format(b, "08b") for b in message_encoded]


input_bits = (
    "0" * N + "".join(reversed(message_bytes[1:])) + "0" * (B - R) + message_bytes[0]
)

spongent_circuit, register_mapping = spongent_circuit(message_size)
result = spongent_circuit.run(input_bits)

state = [None] * B
for position, bit in zip(register_mapping, reversed(result[-B:])):
    state[position] = bit

state_hex = ba2hex(bitarray("".join(map(str, reversed(state))))).upper()

output = result[0:N]
output_hex = ba2hex(bitarray("".join(map(str, output)))).upper()

if not quiet:
    print(f"Message(String) :{message}")
    print(f"Message(Hex)    :{message_encoded.hex().upper()}")
    print(f"Hash            :{output_hex}")
    print(f"State           :{state_hex}")
else:
    print(output_hex)
