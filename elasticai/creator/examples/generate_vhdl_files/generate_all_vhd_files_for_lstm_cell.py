import sys
import os
from argparse import ArgumentParser
import shutil

from elasticai.creator.vhdl.generator.generator_functions_for_one_lstm_cell import (
    generate_rom_file,
    inference_model,
    define_weights_and_bias,
)
from paths import ROOT_DIR
import torch
import random
import numpy as np
from elasticai.creator.layers import QLSTMCell
from elasticai.creator.vhdl.generator.generator_functions import get_file_path_string
from elasticai.creator.vhdl.vhdl_formatter.vhdl_formatter import format_vhdl
from elasticai.creator.vhdl.generator.lstm_testbench_generator import LSTMCellTestBench
from elasticai.creator.vhdl.generator.precomputed_scalar_function import Sigmoid, Tanh

"""
this module generates all vhd files for a single lstm cell
"""


def define_lstm_cell(input_size: int, hidden_size: int) -> QLSTMCell:
    """
    returns a QLSTM Cell with the given input and hidden size
    Args:
        input_size (int): input size of QLSTM Cell
        hidden_size (int): hidden size of QLSTM Cell
    Returns:
        returns the corresponding QLSTM Cell
    """
    return QLSTMCell(
        input_size=input_size,
        hidden_size=hidden_size,
        state_quantizer=lambda x: x,
        weight_quantizer=lambda x: x,
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "--path",
        help="relative path from project root to folder for generated vhd files",
        required=True,
    )
    args = arg_parser.parse_args(args)
    if not os.path.isdir(ROOT_DIR + "/" + args.path):
        os.mkdir(ROOT_DIR + "/" + args.path)

    ### set the current values ###
    torch.manual_seed(0)
    random.seed(0)
    current_frac_bits = 8
    current_nbits = 16
    current_input_size = 5
    current_hidden_size = 20
    current_len_weights = (
        current_input_size + current_hidden_size
    ) * current_hidden_size
    current_len_bias = current_hidden_size

    lstm_cell = define_lstm_cell(current_input_size, current_hidden_size)
    weights_list, bias_list = define_weights_and_bias(
        lstm_cell,
        current_frac_bits,
        current_nbits,
        current_len_weights,
        current_len_bias,
    )
    print("weights_list", weights_list)
    print("bias_list", bias_list)
    x_h_test_input, c_test_input, h_output = inference_model(
        lstm_cell,
        current_frac_bits,
        current_nbits,
        current_input_size,
        current_hidden_size,
    )
    print("x_h_test_input", x_h_test_input)
    print("c_test_input", c_test_input)
    print("h_output", h_output)

    ### generate source files for use-case ###

    ## generate weights source files ##
    weight_name_index_dict = {0: "wi", 1: "wf", 2: "wg", 3: "wo"}
    for key, value in weight_name_index_dict.items():
        file_path_weight = get_file_path_string(
            relative_path_from_project_root=args.path,
            file_name=value + "_rom.vhd",
        )
        generate_rom_file(
            file_path=file_path_weight,
            weights_or_bias_list=weights_list,
            nbits=current_nbits,
            name=value,
            index=key,
        )

    ## generate bias source files ##
    bias_name_index_dict = {0: "bi", 1: "bf", 2: "bg", 3: "bo"}
    for key, value in bias_name_index_dict.items():
        file_path_bias = get_file_path_string(
            relative_path_from_project_root=args.path,
            file_name=value + "_rom.vhd",
        )
        generate_rom_file(
            file_path=file_path_bias,
            weights_or_bias_list=bias_list,
            nbits=current_nbits,
            name=value,
            index=key,
        )

    ## generate sigmoid and tanh activation source files ##
    file_path_sigmoid = get_file_path_string(
        relative_path_from_project_root=args.path,
        file_name="sigmoid.vhd",
    )

    with open(file_path_sigmoid, "w") as writer:
        sigmoid = Sigmoid(
            data_width=current_nbits,
            frac_width=current_frac_bits,
            x=np.linspace(-2.5, 2.5, 256),
        )
        sigmoid_code = sigmoid()
        for line in sigmoid_code:
            writer.write(line + "\n")

    file_path_tanh = get_file_path_string(
        relative_path_from_project_root=args.path,
        file_name="tanh.vhd",
    )

    with open(file_path_tanh, "w") as writer:
        tanh = Tanh(
            data_width=current_nbits,
            frac_width=current_frac_bits,
            x=np.linspace(-1, 1, 256),
        )
        tanh_code = tanh()
        for line in tanh_code:
            writer.write(line + "\n")

    ### generate testbench file for use-case ###
    file_path_testbench = get_file_path_string(
        relative_path_from_project_root=args.path,
        file_name="lstm_cell_tb.vhd",
    )

    with open(file_path_testbench, "w") as writer:
        lstm_cell = LSTMCellTestBench(
            data_width=current_nbits,
            frac_width=current_frac_bits,
            input_size=current_input_size,
            hidden_size=current_hidden_size,
            test_x_h_data=x_h_test_input,
            test_c_data=c_test_input,
            h_out=list(h_output),
            component_name="lstm_cell",
        )
        lstm_cell_code = lstm_cell()
        for line in lstm_cell_code:
            writer.write(line + "\n")

    # indent all lines of the files
    for value in weight_name_index_dict.values():
        file_path_weight = get_file_path_string(
            relative_path_from_project_root=args.path,
            file_name=value + "_rom.vhd",
        )
        format_vhdl(file_path=file_path_weight)
    for value in bias_name_index_dict.values():
        file_path_bias = get_file_path_string(
            relative_path_from_project_root=args.path,
            file_name=value + "_rom.vhd",
        )
        format_vhdl(file_path=file_path_bias)

    format_vhdl(file_path=file_path_sigmoid)
    format_vhdl(file_path=file_path_tanh)
    format_vhdl(file_path=file_path_testbench)

    ### copy static files ###
    for filename in os.listdir(ROOT_DIR + "/vhd_files/static_files/"):
        shutil.copy(
            ROOT_DIR + "/vhd_files/static_files/" + filename,
            ROOT_DIR + "/" + args.path,
        )