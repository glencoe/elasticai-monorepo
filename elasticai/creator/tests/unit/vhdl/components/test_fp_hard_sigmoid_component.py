import unittest

from elasticai.creator.hdl.vhdl.code_files import FPHardSigmoidComponent
from elasticai.creator.vhdl.number_representations import FixedPoint


class FPHardSigmoidComponentTest(unittest.TestCase):
    def test_hard_sigmoid_correct_number_of_lines(self) -> None:
        to_fp = FixedPoint.get_builder(total_bits=8, frac_bits=4)

        component = FPHardSigmoidComponent(
            layer_id="0",
            zero_threshold=to_fp(-3),
            one_threshold=to_fp(3),
            slope=to_fp(0.15),
            y_intercept=to_fp(0.5),
            fixed_point_factory=to_fp,
        )

        self.assertEqual(len(list(component.lines())), 88)
