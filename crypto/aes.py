import numpy as np
from utils.math_utils import galois_multiply
from crypto.box import SBOX, INV_SBOX


class AESCipher:
    def __init__(self):
        # Initialize S-box
        self.sbox = SBOX

        # Initialize inverse S-box
        self.inv_sbox = INV_SBOX

        # Rcon used in key expansion
        self.rcon = np.array(
            [
                [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36],
                [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            ],
            dtype=np.uint8,
        )

    def sub_bytes(self, state):
        """Substitute bytes using the S-box"""
        rows, cols = state.shape
        result = np.zeros_like(state)

        for i in range(rows):
            for j in range(cols):
                # Extract row and column from the current byte value
                x = (state[i, j] >> 4) & 0x0F  # Row in S-box (high 4 bits)
                y = state[i, j] & 0x0F  # Column in S-box (low 4 bits)
                result[i, j] = self.sbox[x, y]

        return result

    def inv_sub_bytes(self, state):
        """Substitute bytes using the inverse S-box"""
        rows, cols = state.shape
        result = np.zeros_like(state)

        for i in range(rows):
            for j in range(cols):
                x = (state[i, j] >> 4) & 0x0F
                y = state[i, j] & 0x0F
                result[i, j] = self.inv_sbox[x, y]

        return result

    def shift_rows(self, state):
        """Shift rows of state matrix"""
        result = state.copy()

        # No shift for row 0
        # Shift row 1 by 1
        result[1] = np.roll(result[1], -1)
        # Shift row 2 by 2
        result[2] = np.roll(result[2], -2)
        # Shift row 3 by 3
        result[3] = np.roll(result[3], -3)

        return result

    def inv_shift_rows(self, state):
        """Inverse shift rows of state matrix"""
        result = state.copy()

        # No shift for row 0
        # Shift row 1 by 1 to the right
        result[1] = np.roll(result[1], 1)
        # Shift row 2 by 2 to the right
        result[2] = np.roll(result[2], 2)
        # Shift row 3 by 3 to the right
        result[3] = np.roll(result[3], 3)

        return result

    def mix_columns(self, state):
        """Mix the columns of the state matrix"""
        result = np.zeros_like(state)

        for i in range(4):  # For each column
            result[0, i] = (
                galois_multiply(0x02, state[0, i])
                ^ galois_multiply(0x03, state[1, i])
                ^ state[2, i]
                ^ state[3, i]
            )
            result[1, i] = (
                state[0, i]
                ^ galois_multiply(0x02, state[1, i])
                ^ galois_multiply(0x03, state[2, i])
                ^ state[3, i]
            )
            result[2, i] = (
                state[0, i]
                ^ state[1, i]
                ^ galois_multiply(0x02, state[2, i])
                ^ galois_multiply(0x03, state[3, i])
            )
            result[3, i] = (
                galois_multiply(0x03, state[0, i])
                ^ state[1, i]
                ^ state[2, i]
                ^ galois_multiply(0x02, state[3, i])
            )

        return result

    def inv_mix_columns(self, state):
        """Inverse mix the columns of the state matrix"""
        result = np.zeros_like(state)

        for i in range(4):  # For each column
            result[0, i] = (
                galois_multiply(0x0E, state[0, i])
                ^ galois_multiply(0x0B, state[1, i])
                ^ galois_multiply(0x0D, state[2, i])
                ^ galois_multiply(0x09, state[3, i])
            )
            result[1, i] = (
                galois_multiply(0x09, state[0, i])
                ^ galois_multiply(0x0E, state[1, i])
                ^ galois_multiply(0x0B, state[2, i])
                ^ galois_multiply(0x0D, state[3, i])
            )
            result[2, i] = (
                galois_multiply(0x0D, state[0, i])
                ^ galois_multiply(0x09, state[1, i])
                ^ galois_multiply(0x0E, state[2, i])
                ^ galois_multiply(0x0B, state[3, i])
            )
            result[3, i] = (
                galois_multiply(0x0B, state[0, i])
                ^ galois_multiply(0x0D, state[1, i])
                ^ galois_multiply(0x09, state[2, i])
                ^ galois_multiply(0x0E, state[3, i])
            )

        return result

    def add_round_key(self, state, round_key):
        """Add round key to state by XORing"""
        return state ^ round_key

    def key_expansion(self, key):
        """Expand the key into the key schedule"""
        Nk = 4  # Key length in 32-bit words (AES-128)
        Nr = 10  # Number of rounds (AES-128)

        # Key size in 32-bit words
        key_schedule = np.zeros((4, 4 * (Nr + 1)), dtype=np.uint8)

        # Copy the initial key into the first Nk columns of the key schedule
        key_schedule[:, 0:Nk] = key.reshape(4, Nk)

        # Generate the remaining words of the key schedule
        for i in range(Nk, 4 * (Nr + 1)):
            temp = key_schedule[:, i - 1].copy()

            if i % Nk == 0:
                # Rotate word
                temp = np.roll(temp, -1)

                # SubWord
                for j in range(4):
                    row = (temp[j] >> 4) & 0x0F
                    col = temp[j] & 0x0F
                    temp[j] = self.sbox[row, col]

                # XOR with Rcon
                temp[0] ^= self.rcon[0, i // Nk - 1]

            key_schedule[:, i] = key_schedule[:, i - Nk] ^ temp

        return key_schedule

    def encrypt(self, plaintext, key):
        """Encrypt a 16-byte block using AES-128"""
        # Convert key to numpy array of uint8
        if isinstance(key, bytes) or isinstance(key, bytearray):
            key_array = np.frombuffer(key, dtype=np.uint8)
        else:
            key_array = np.array(key, dtype=np.uint8)

        # Reshape to 4x4 matrix (column-major order)
        key_matrix = key_array.reshape(4, 4)

        # Convert plaintext to numpy array and reshape
        if isinstance(plaintext, bytes) or isinstance(plaintext, bytearray):
            plaintext_array = np.frombuffer(plaintext, dtype=np.uint8)
        else:
            plaintext_array = np.array(plaintext, dtype=np.uint8)

        state = plaintext_array.reshape(4, 4)

        # Key expansion
        key_schedule = self.key_expansion(key_matrix)

        # Initial round
        state = self.add_round_key(state, key_schedule[:, 0:4])

        # Main rounds
        for round_num in range(1, 10):
            state = self.sub_bytes(state)
            state = self.shift_rows(state)
            state = self.mix_columns(state)
            state = self.add_round_key(
                state, key_schedule[:, 4 * round_num : 4 * (round_num + 1)]
            )

        # Final round (no mix columns)
        state = self.sub_bytes(state)
        state = self.shift_rows(state)
        state = self.add_round_key(state, key_schedule[:, 40:44])

        # Convert back to 1D array
        return state.flatten()

    def decrypt(self, ciphertext, key):
        """Decrypt a 16-byte block using AES-128"""
        # Convert key to numpy array of uint8
        if isinstance(key, bytes) or isinstance(key, bytearray):
            key_array = np.frombuffer(key, dtype=np.uint8)
        else:
            key_array = np.array(key, dtype=np.uint8)

        # Reshape to 4x4 matrix (column-major order)
        key_matrix = key_array.reshape(4, 4)

        # Convert ciphertext to numpy array and reshape
        if isinstance(ciphertext, bytes) or isinstance(ciphertext, bytearray):
            ciphertext_array = np.frombuffer(ciphertext, dtype=np.uint8)
        else:
            ciphertext_array = np.array(ciphertext, dtype=np.uint8)

        state = ciphertext_array.reshape(4, 4)

        # Key expansion
        key_schedule = self.key_expansion(key_matrix)

        # Initial round
        state = self.add_round_key(state, key_schedule[:, 40:44])

        # Main rounds
        for round_num in range(9, 0, -1):
            state = self.inv_shift_rows(state)
            state = self.inv_sub_bytes(state)
            state = self.add_round_key(
                state, key_schedule[:, 4 * round_num : 4 * (round_num + 1)]
            )
            state = self.inv_mix_columns(state)

        # Final round
        state = self.inv_shift_rows(state)
        state = self.inv_sub_bytes(state)
        state = self.add_round_key(state, key_schedule[:, 0:4])

        # Convert back to 1D array
        return state.flatten()
