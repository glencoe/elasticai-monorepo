from unittest import TestCase

from elasticai.creator.vhdl.number_representations import (
    FixedPoint,
    FloatToSignedFixedPointConverter,
    ToLogicEncoder,
    hex_representation,
    two_complements_representation,
)


class FixedPointTest(TestCase):
    def test_zero(self):
        fp_value = FixedPoint(0, total_bits=1, frac_bits=0)
        self.assertEqual(0, int(fp_value))

    def test_1_with_8_total_bits_3_frac_bits(self):
        fp_value = FixedPoint(1, total_bits=8, frac_bits=3)
        self.assertEqual(8, int(fp_value))

    def test_minus_1_with_8_total_bits_3_frac_bits_signed(self):
        fp_value = FixedPoint(-1, total_bits=8, frac_bits=3, signed=True)
        self.assertEqual(-8, int(fp_value))

    def test_minus_1_with_8_total_bits_3_frac_bits_unsigned(self):
        fp_value = FixedPoint(-1, total_bits=8, frac_bits=3)
        self.assertEqual(248, int(fp_value))

    def test_minus_3_21_with_16_total_bits_12_frac_bits_unsigned(self):
        fp_value = FixedPoint(-3.21, total_bits=16, frac_bits=12)
        self.assertEqual(52388, int(fp_value))

    def test_initialize_with_value_not_in_range(self):
        with self.assertRaises(ValueError):
            _ = FixedPoint(100, total_bits=4, frac_bits=2)

    def test_fixed_point_to_float_3_2_signed(self):
        fp_value = FixedPoint(3.2, total_bits=8, frac_bits=4, signed=True)
        self.assertAlmostEqual(3.2, float(fp_value), places=1)

    def test_fixed_point_to_float_5_36_unsigned(self):
        fp_value = FixedPoint(5.36, total_bits=12, frac_bits=6)
        self.assertAlmostEqual(5.36, float(fp_value), places=2)

    def test_fixed_point_to_float_minus_5_36_unsigned(self):
        fp_value = FixedPoint(-5.36, total_bits=16, frac_bits=12)
        self.assertAlmostEqual(-5.36, float(fp_value), places=2)

    def test_to_hex_zero_with_one_bits(self):
        fp_value = FixedPoint(0, total_bits=1, frac_bits=0)
        self.assertEqual('x"0"', fp_value.to_hex())

    def test_to_hex_zero_with_six_bits(self):
        fp_value = FixedPoint(0, total_bits=6, frac_bits=0)
        self.assertEqual('x"00"', fp_value.to_hex())

    def test_to_hex_zero_with_sixteen_bits(self):
        fp_value = FixedPoint(0, total_bits=16, frac_bits=0)
        self.assertEqual('x"0000"', fp_value.to_hex())

    def test_to_hex_minus_one_with_sixteen_bits(self):
        fp_value = FixedPoint(-1, total_bits=16, frac_bits=0)
        self.assertEqual('x"ffff"', fp_value.to_hex())

    def test_to_hex_minus_three_with_three_bits(self):
        fp_value = FixedPoint(-3, total_bits=3, frac_bits=0)
        self.assertEqual('x"5"', fp_value.to_hex())

    def test_to_hex_minus_254_with_sixteen_bits(self):
        fp_value = FixedPoint(-254, total_bits=16, frac_bits=0)
        self.assertEqual('x"ff02"', fp_value.to_hex())

    def test_to_hex_minus_19_5_with_16_bits(self):
        fp_value = FixedPoint(-19.5, total_bits=16, frac_bits=8)
        self.assertEqual('x"ec80"', fp_value.to_hex())

    def test_to_bin_zero_with_one_bits(self):
        fp_value = FixedPoint(0, total_bits=1, frac_bits=0)
        self.assertEqual("0", fp_value.to_bin())

    def test_to_bin_zero_with_three_bits(self):
        fp_value = FixedPoint(0, total_bits=3, frac_bits=0)
        self.assertEqual("000", fp_value.to_bin())

    def test_to_bin_five_with_four_bits(self):
        fp_value = FixedPoint(5, total_bits=4, frac_bits=0)
        self.assertEqual("0101", fp_value.to_bin())

    def test_to_bin_minus_one_with_two_bits(self):
        fp_value = FixedPoint(-1, total_bits=2, frac_bits=0)
        self.assertEqual("11", fp_value.to_bin())

    def test_to_bin_minus_two_with_two_bits(self):
        fp_value = FixedPoint(-2, total_bits=2, frac_bits=0)
        self.assertEqual("10", fp_value.to_bin())

    def test_to_bin_minus_256_with_sixteen_bits(self):
        fp_value = FixedPoint(-256, total_bits=16, frac_bits=0)
        self.assertEqual("1111111100000000", fp_value.to_bin())

    def test_to_bin_minus_254_with_sixteen_bits(self):
        fp_value = FixedPoint(-254, total_bits=16, frac_bits=0)
        self.assertEqual("1111111100000010", fp_value.to_bin())

    def test_to_bin_minus_19_5_with_16_bits(self):
        fp_value = FixedPoint(-19.5, total_bits=16, frac_bits=8)
        self.assertEqual("1110110010000000", fp_value.to_bin())

    def test_from_int_signed(self):
        fp_value = FixedPoint.from_int(-13148, total_bits=16, frac_bits=12, signed=True)
        self.assertAlmostEqual(-3.21, float(fp_value), places=2)

    def test_from_int_unsigned(self):
        fp_value = FixedPoint.from_int(52388, total_bits=16, frac_bits=12)
        self.assertAlmostEqual(-3.21, float(fp_value), places=2)

    def test_repr(self):
        fp_value = FixedPoint(
            value=3.2, total_bits=8, frac_bits=4, signed=True, strict=False
        )
        target_repr = "FixedPoint(value=3.2, total_bits=8, frac_bits=4, signed=True, strict=False)"
        self.assertEqual(target_repr, repr(fp_value))

    def test_str(self):
        fp_value = FixedPoint(-5, total_bits=8, frac_bits=4, signed=True)
        target_str = "-80"
        self.assertEqual(target_str, str(fp_value))


class FixedPointConverterTest(TestCase):
    def test_get_zero(self):
        f = FloatToSignedFixedPointConverter(bits_used_for_fraction=0)
        self.assertEqual(0, f(0))

    def test_get_one_with_2bits_for_fraction(self):
        f = FloatToSignedFixedPointConverter(bits_used_for_fraction=2)
        self.assertEqual(1 << 2, f(1))

    def test_get_one_with_3bits_for_fraction(self):
        f = FloatToSignedFixedPointConverter(bits_used_for_fraction=3)
        self.assertEqual(1 << 3, f(1))

    def test_raise_error_if_not_convertible(self):
        f = FloatToSignedFixedPointConverter(bits_used_for_fraction=0)
        try:
            f(0.5)
            self.fail()
        except ValueError as e:
            self.assertEqual(
                "0.5 not convertible to fixed point number using 0 bits for fractional part",
                str(e),
            )


class BinaryTwoComplementRepresentation(TestCase):
    def test_zero_with_zero_bits(self):
        with self.assertRaises(ValueError):
            _ = two_complements_representation(0, num_bits=0)

    def test_five_with_minus_one_bits(self):
        with self.assertRaises(ValueError):
            _ = two_complements_representation(5, num_bits=-1)

    def test_zero_with_one_bits(self):
        actual = two_complements_representation(0, num_bits=1)
        expected = "0"
        self.assertEqual(expected, actual)

    def test_zero_with_three_bits(self):
        actual = two_complements_representation(0, num_bits=3)
        expected = "000"
        self.assertEqual(expected, actual)

    def test_five_with_four_bits(self):
        actual = two_complements_representation(5, num_bits=4)
        expected = "0101"
        self.assertEqual(expected, actual)

    def test_one(self):
        actual = two_complements_representation(1, 1)
        expected = "1"
        self.assertEqual(expected, actual)

    def test_minus_one(self):
        actual = two_complements_representation(-1, 2)
        expected = "11"
        self.assertEqual(expected, actual)

    def test_minus_two(self):
        actual = two_complements_representation(-2, 2)
        expected = "10"
        self.assertEqual(expected, actual)

    def test_two(self):
        actual = two_complements_representation(2, 3)
        expected = "010"
        self.assertEqual(expected, actual)

    def test_minus_four(self):
        actual = two_complements_representation(-4, 3)
        expected = "100"
        self.assertEqual(expected, actual)

    def test_minus_three_three_bit(self):
        actual = two_complements_representation(-3, 3)
        expected = "101"
        self.assertEqual(expected, actual)

    def test_minus_256_16_bit(self):
        actual = two_complements_representation(-256, 16)
        expected = "1111111100000000"
        self.assertEqual(expected, actual)

    def test_minus_254_16_bit(self):
        actual = two_complements_representation(-254, 16)
        expected = "1111111100000010"
        self.assertEqual(expected, actual)


class HexRepresentation(TestCase):
    def test_zero_with_zero_bits(self):
        with self.assertRaises(ValueError):
            _ = hex_representation(0, num_bits=0)

    def test_five_with_minus_one_bits(self):
        with self.assertRaises(ValueError):
            _ = hex_representation(5, num_bits=-1)

    def test_zero_with_one_bits(self):
        actual = hex_representation(0, num_bits=1)
        expected = 'x"0"'
        self.assertEqual(expected, actual)

    def test_zero_with_seven_bits(self):
        actual = hex_representation(0, num_bits=7)
        expected = 'x"00"'
        self.assertEqual(expected, actual)

    def test_one(self):
        actual = hex_representation(1, 16)
        expected = 'x"0001"'
        self.assertEqual(expected, actual)

    def test_minus_one(self):
        actual = hex_representation(-1, 16)
        expected = 'x"ffff"'
        self.assertEqual(expected, actual)

    def test_two(self):
        actual = hex_representation(2, 16)
        expected = 'x"0002"'
        self.assertEqual(expected, actual)

    def test_minus_two(self):
        actual = hex_representation(-2, 16)
        expected = 'x"fffe"'
        self.assertEqual(expected, actual)

    def test_minus_four_four_bit(self):
        actual = hex_representation(-4, 4)
        expected = 'x"c"'
        self.assertEqual(expected, actual)

    def test_minus_three_three_bit(self):
        actual = hex_representation(-3, 3)
        expected = 'x"5"'
        self.assertEqual(expected, actual)

    def test_minus_256_16_bit(self):
        actual = hex_representation(-256, 16)
        expected = 'x"ff00"'
        self.assertEqual(expected, actual)

    def test_minus_254_16_bit(self):
        actual = hex_representation(-254, 16)
        expected = 'x"ff02"'
        self.assertEqual(expected, actual)

    def test_255_with_12_bits(self):
        actual = hex_representation(255, num_bits=12)
        expected = 'x"0ff"'
        self.assertEqual(expected, actual)


class NumberEncoderTest(TestCase):
    """
    Test Cases:
      - build new encoder from existing encoder ensuring compatibility of enumerations
        Use case scenario: Connecting the outputs of layer h_1 to the inputs of layer h_2, while we can consider the in-
         and output as enumerations, ie. we don't care about the actual numeric values. However to still allow for
         max pooling operations we might want to ensure that the encoding is monotonous.
    """

    def test_binarization_minus_one_is_zero(self):
        encoder = ToLogicEncoder()
        encoder.register_symbol(-1)
        self.assertEqual(0, encoder[-1])

    def test_binarization_minus_1_to_0_and_1to1(self):
        encoder = ToLogicEncoder()
        encoder.register_symbol(-1)
        encoder.register_symbol(1)
        self.assertEqual(1, encoder[1])

    def test_encoder_is_monotonous(self):
        encoder = ToLogicEncoder()
        encoder.register_symbol(1)
        encoder.register_symbol(-1)
        self.assertEqual(1, encoder[1])

    def test_encoder_to_bit_vector(self):
        encoder = ToLogicEncoder()
        encoder.register_symbol(1)
        encoder.register_symbol(-1)
        bits = encoder(-1)
        self.assertEqual("0", bits)

    def test_ternarization_minus1_to_00(self):
        encoder = ToLogicEncoder()
        encoder.register_symbol(-1)
        encoder.register_symbol(0)
        encoder.register_symbol(1)
        test_parameters = (
            (0, -1),
            (1, 0),
            (2, 1),
        )
        for parameter in test_parameters:
            with self.subTest(parameter):
                expected = parameter[0]
                actual = encoder[parameter[1]]
                self.assertEqual(expected, actual)

    def test_registering_numbers_in_batch(self):
        one_by_one = ToLogicEncoder()
        by_batch = ToLogicEncoder()
        batch = [1, 0, -1]
        for number in batch:
            one_by_one.register_symbol(number)
        by_batch.register_symbols(batch)
        self.assertTrue(
            by_batch == one_by_one,
            "expected: {}, actual: {}".format(one_by_one, by_batch),
        )
