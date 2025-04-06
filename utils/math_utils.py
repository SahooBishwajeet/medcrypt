def galois_multiply(a, b):
    """Multiplication in GF(2^8)

    This implements the multiplication of two elements in the Galois Field GF(2^8)
    defined with the irreducible polynomial x^8 + x^4 + x^3 + x + 1.
    """
    p = 0

    for i in range(8):
        if b & 1:  # If the lowest bit of b is 1
            p ^= a  # XOR with a

        # Check if the leftmost bit of a is 1
        high_bit = a & 0x80

        # Shift a left by 1
        a <<= 1
        a &= 0xFF  # Ensure a stays within 8 bits

        # If the high bit was 1, perform reduction
        if high_bit:
            # XOR with the irreducible polynomial 0x1B
            # (represents x^4 + x^3 + x + 1)
            a ^= 0x1B

        # Shift b right by 1
        b >>= 1

    return p
