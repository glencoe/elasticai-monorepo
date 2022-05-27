import os
from argparse import ArgumentParser

from elasticai.creator.vhdl.precomputed_scalar_function import (
    PrecomputedScalarTestBench,
)
from elasticai.creator.vhdl.vhdl_formatter.vhdl_formatter import format_vhdl


def main() -> None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "--path",
        help="path to folder for generated vhd files",
        required=True,
    )
    args = arg_parser.parse_args()
    if not os.path.isdir(args.path):
        os.mkdir(args.path)
    component_name = "tanh_tb"
    file_path = os.path.join(args.path, f"{component_name}.vhd")

    with open(file_path, "w") as writer:
        tanh = PrecomputedScalarTestBench(
            component_name=component_name,
            data_width=16,
            frac_width=8,
            x_list_for_testing=[-1281, -1000, -500, 0, 500, 800, 1024],
            y_list_for_testing=["1111111100000000", -255, -246, 0, 245, 254, 255],
        )
        tanh_code = tanh()
        for line in tanh_code:
            writer.write(line + "\n")

    format_vhdl(file_path=file_path)


if __name__ == "__main__":
    main()
