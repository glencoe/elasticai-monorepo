import numpy as np

from elasticai.creator.vhdl.generator.precomputed_scalar_function import Tanh
from elasticai.creator.vhdl.generator.generator_functions import get_file_path_string


def main():
    file_path = get_file_path_string(
        folder_names=["..", "source"], file_name="tanh.vhd"
    )
    tanh = Tanh(data_width=16, frac_width=8, x=np.linspace(-5, 5, 259))
    with open(file_path, "w") as writer:
        tanh_code = tanh()
        for line in tanh_code:
            writer.write(line + "\n")


if __name__ == "__main__":
    main()