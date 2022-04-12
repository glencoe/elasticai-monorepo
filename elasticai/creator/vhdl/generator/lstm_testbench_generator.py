from itertools import chain
from typing import Iterable
import math

from elasticai.creator.vhdl.language import (
    ContextClause,
    LibraryClause,
    UseClause,
    Entity,
    Architecture,
    ComponentDeclaration,
    Process,
    PortMap,
    form_to_hex_list,
)
from elasticai.creator.vhdl.language_testbench import (
    TestCasesLSTMCommonGate,
    TestCasesLSTMCell,
    Procedure,
)


class LSTMCommonGateTestBench:
    def __init__(
        self,
        data_width: int,
        frac_width: int,
        vector_len_width: int,
        x_mem_list_for_testing: list,
        w_mem_list_for_testing: list,
        b_list_for_testing: list,
        y_list_for_testing: list[int],
        component_name: str = None,
    ):
        self.component_name = self._get_lower_case_class_name_or_component_name(
            component_name=component_name
        )
        self.data_width = data_width
        self.frac_width = frac_width
        self.vector_len_width = vector_len_width
        self.x_mem_list_for_testing = x_mem_list_for_testing
        self.w_mem_list_for_testing = w_mem_list_for_testing
        self.y_list_for_testing = y_list_for_testing
        self.b_list_for_testing = b_list_for_testing

    @classmethod
    def _get_lower_case_class_name_or_component_name(cls, component_name):
        if component_name is None:
            return cls.__name__.lower()
        return component_name

    @property
    def file_name(self) -> str:
        return f"{self.component_name}_tb.vhd"

    def __call__(self) -> Iterable[str]:
        library = ContextClause(
            library_clause=LibraryClause(logical_name_list=["ieee"]),
            use_clause=UseClause(
                selected_names=[
                    "ieee.std_logic_1164.all",
                    "ieee.numeric_std.all",
                    "ieee.math_real.all",
                ]
            ),
        )

        entity = Entity(self.component_name + "_tb")
        entity.generic_list = [
            f"DATA_WIDTH : integer := {self.data_width}",
            f"FRAC_WIDTH : integer := {self.frac_width}",
            f"VECTOR_LEN_WIDTH : integer := {self.vector_len_width}",
        ]
        entity.port_list = [
            "clk : out std_logic",
        ]

        component = ComponentDeclaration(identifier=self.component_name)
        component.generic_list = [
            f"DATA_WIDTH : integer := {self.data_width}",
            f"FRAC_WIDTH : integer := {self.frac_width}",
            f"VECTOR_LEN_WIDTH : integer := {self.vector_len_width}",
        ]
        component.port_list = [
            "reset : in std_logic",
            "clk : in std_logic",
            "x : in signed(DATA_WIDTH-1 downto 0)",
            "w : in signed(DATA_WIDTH-1 downto 0)",
            "b : in signed(DATA_WIDTH-1 downto 0)",
            "vector_len : in unsigned(VECTOR_LEN_WIDTH-1 downto 0)",
            "idx : out unsigned(VECTOR_LEN_WIDTH-1 downto 0)",
            "ready : out std_logic",
            "y : out signed(DATA_WIDTH-1 downto 0)",
        ]

        process = Process(
            identifier="clock",
        )
        process.process_statements_list = [
            "clk <= '0'",
            "wait for clk_period/2",
            "clk <= '1'",
            "wait for clk_period/2",
        ]

        uut_port_map = PortMap(map_name="uut", component_name=self.component_name)
        uut_port_map.signal_list.append("reset => reset")
        uut_port_map.signal_list.append("clk => clock")
        uut_port_map.signal_list.append("x => x")
        uut_port_map.signal_list.append("w => w")
        uut_port_map.signal_list.append("b => b")
        uut_port_map.signal_list.append("vector_len => vector_len")
        uut_port_map.signal_list.append("idx => idx")
        uut_port_map.signal_list.append("ready => ready")
        uut_port_map.signal_list.append("y => y")

        test_cases = TestCasesLSTMCommonGate(
            x_mem_list_for_testing=self.x_mem_list_for_testing,
            w_mem_list_for_testing=self.w_mem_list_for_testing,
            b_list_for_testing=self.b_list_for_testing,
            y_list_for_testing=self.y_list_for_testing,
        )
        test_process = Process(identifier="test")
        test_process.process_test_case_list = test_cases

        architecture = Architecture(
            design_unit=self.component_name + "_tb",
        )

        architecture.architecture_declaration_list.append(
            "type RAM_ARRAY is array (0 to 9) of signed(DATA_WIDTH-1 downto 0)"
        )

        architecture.architecture_declaration_list.append(
            "signal clk_period : time := 2 ps"
        )
        architecture.architecture_declaration_list.append("signal clock : std_logic")
        architecture.architecture_declaration_list.append(
            "signal reset, ready : std_logic:='0'"
        )
        architecture.architecture_declaration_list.append(
            "signal X_MEM : RAM_ARRAY :=(others=>(others=>'0'))"
        )
        architecture.architecture_declaration_list.append(
            "signal W_MEM : RAM_ARRAY:=(others=>(others=>'0'))"
        )
        architecture.architecture_declaration_list.append(
            "signal x, w, y, b : signed(DATA_WIDTH-1 downto 0):=(others=>'0')"
        )
        architecture.architecture_declaration_list.append(
            "signal vector_len : unsigned(VECTOR_LEN_WIDTH-1 downto 0):=(others=>'0')"
        )
        architecture.architecture_declaration_list.append(
            "signal idx : unsigned(VECTOR_LEN_WIDTH-1 downto 0):=(others=>'0')"
        )
        architecture.architecture_component_list.append(component)
        architecture.architecture_process_list.append(process)
        architecture.architecture_port_map_list.append(uut_port_map)
        architecture.architecture_assignment_at_end_of_declaration_list.append(
            "x <= X_MEM(to_integer(idx))"
        )
        architecture.architecture_assignment_at_end_of_declaration_list.append(
            "w <= W_MEM(to_integer(idx))"
        )
        architecture.architecture_statement_part = test_process

        code = chain(chain(library(), entity()), architecture())
        return code


class LSTMCellTestBench:
    def __init__(
        self,
        data_width: int,
        frac_width: int,
        input_size: int,
        hidden_size: int,
        test_x_h_data: list[str],
        test_c_data: list[str],
        h_out: list[int],
        component_name: str = None,
    ):
        self.component_name = self._get_lower_case_class_name_or_component_name(
            component_name=component_name
        )
        self.data_width = data_width
        self.frac_width = frac_width
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.x_h_addr_width = math.ceil(math.log2(input_size + hidden_size))
        self.hidden_addr_widht = math.ceil(math.log2(hidden_size))
        self.w_addr_width = math.ceil(
            math.log2((input_size + hidden_size) * hidden_size)
        )
        self.test_x_h_data = test_x_h_data
        self.test_c_data = test_c_data
        self.h_out = h_out

    @classmethod
    def _get_lower_case_class_name_or_component_name(cls, component_name):
        if component_name is None:
            return cls.__name__.lower()
        return component_name

    @property
    def file_name(self) -> str:
        return f"{self.component_name}_tb.vhd"

    def __call__(self) -> Iterable[str]:
        library = ContextClause(
            library_clause=LibraryClause(logical_name_list=["ieee", "work"]),
            use_clause=UseClause(
                selected_names=[
                    "ieee.std_logic_1164.all",
                    "ieee.numeric_std.all",
                    "work.lstm_common.all",
                ]
            ),
        )

        entity = Entity(self.component_name + "_tb")
        entity.generic_list = [
            f"DATA_WIDTH : integer := {self.data_width}",
            f"FRAC_WIDTH : integer := {self.frac_width}",
            f"INPUT_SIZE : integer := {self.input_size}",
            f"HIDDEN_SIZE : integer := {self.hidden_size}",
            f"X_H_ADDR_WIDTH : integer := {self.x_h_addr_width}",
            f"HIDDEN_ADDR_WIDTH : integer := {self.hidden_addr_widht}",
            f"W_ADDR_WIDTH : integer := {self.w_addr_width}",
        ]
        entity.port_list = [
            "clk : out std_logic",
        ]

        procedure_0 = Procedure(identifier="send_x_h_data")
        procedure_0.declaration_list = [
            "addr_in : in std_logic_vector(X_H_ADDR_WIDTH-1 downto 0)",
            "data_in : in std_logic_vector(DATA_WIDTH-1 downto 0)",
            "signal clock : in std_logic",
            "signal wr : out std_logic",
            "signal addr_out : out std_logic_vector(X_H_ADDR_WIDTH-1 downto 0)",
        ]
        procedure_0.declaration_list_with_is = [
            "signal data_out : out std_logic_vector(DATA_WIDTH-1 downto 0))",
        ]
        procedure_0.statement_list = [
            "addr_out <= addr_in",
            "data_out <= data_in",
            "wait until clock='0'",
            "wr <= '1'",
            "wait until clock='1'",
            "wait until clock='0'",
            "wr <= '0'",
            "wait until clock='1'",
        ]
        procedure_1 = Procedure(identifier="send_c_data")
        procedure_1.declaration_list = [
            "addr_in : in std_logic_vector(HIDDEN_ADDR_WIDTH-1 downto 0)",
            "data_in : in std_logic_vector(DATA_WIDTH-1 downto 0)",
            "signal clock : in std_logic",
            "signal wr : out std_logic",
            "signal addr_out : out std_logic_vector(HIDDEN_ADDR_WIDTH-1 downto 0)",
        ]
        procedure_1.declaration_list_with_is = [
            "signal data_out : out std_logic_vector(DATA_WIDTH-1 downto 0))",
        ]
        procedure_1.statement_list = [
            "addr_out <= addr_in",
            "data_out <= data_in",
            "wait until clock='0'",
            "wr <= '1'",
            "wait until clock='1'",
            "wait until clock='0'",
            "wr <= '0'",
            "wait until clock='1'",
        ]

        process = Process(
            identifier="clock",
        )
        process.process_statements_list = [
            "clock <= '0'",
            "wait for clk_period/2",
            "clock <= '1'",
            "wait for clk_period/2",
        ]

        uut_port_map = PortMap(
            map_name="uut",
            component_name="entity work." + self.component_name + "(rtl)",
        )
        uut_port_map.generic_map_list.append("DATA_WIDTH => DATA_WIDTH")
        uut_port_map.generic_map_list.append("FRAC_WIDTH => FRAC_WIDTH")
        uut_port_map.generic_map_list.append("INPUT_SIZE => INPUT_SIZE")
        uut_port_map.generic_map_list.append("HIDDEN_SIZE => HIDDEN_SIZE")
        uut_port_map.generic_map_list.append("X_H_ADDR_WIDTH => X_H_ADDR_WIDTH")
        uut_port_map.generic_map_list.append("HIDDEN_ADDR_WIDTH => HIDDEN_ADDR_WIDTH")
        uut_port_map.generic_map_list.append("W_ADDR_WIDTH => W_ADDR_WIDTH")
        uut_port_map.signal_list.append("clock => clock")
        uut_port_map.signal_list.append("reset => reset")
        uut_port_map.signal_list.append("enable => enable")
        uut_port_map.signal_list.append("x_h_we => x_config_en")
        uut_port_map.signal_list.append("x_h_data => x_config_data")
        uut_port_map.signal_list.append("x_h_addr => x_config_addr")
        uut_port_map.signal_list.append("c_we => c_config_en")
        uut_port_map.signal_list.append("c_data_in => c_config_data")
        uut_port_map.signal_list.append("c_addr_in => c_config_addr")
        uut_port_map.signal_list.append("done => done")
        uut_port_map.signal_list.append("h_out_en => h_out_en")
        uut_port_map.signal_list.append("h_out_data => h_out_data")
        uut_port_map.signal_list.append("h_out_addr => h_out_addr")

        test_cases = TestCasesLSTMCell(reference_h_out=self.h_out)
        test_process = Process(identifier="test")
        test_process.process_test_case_list = test_cases

        architecture = Architecture(
            design_unit=self.component_name + "_tb",
        )
        architecture.architecture_declaration_list.append(
            "signal clk_period : time := 10 ns"
        )

        architecture.architecture_declaration_list.append("signal clock : std_logic")
        architecture.architecture_declaration_list.append("signal enable : std_logic")
        architecture.architecture_declaration_list.append(
            "signal reset: std_logic:='0'"
        )
        architecture.architecture_declaration_list.append(
            "signal x_config_en: std_logic:='0'"
        )
        architecture.architecture_declaration_list.append(
            "signal x_config_data:std_logic_vector(DATA_WIDTH-1 downto 0):=(others=>'0')"
        )
        architecture.architecture_declaration_list.append(
            "signal x_config_addr:std_logic_vector(X_H_ADDR_WIDTH-1 downto 0) :=(others=>'0')"
        )
        architecture.architecture_declaration_list.append(
            "signal h_config_en: std_logic:='0'"
        )
        architecture.architecture_declaration_list.append(
            "signal h_config_data:std_logic_vector(DATA_WIDTH-1 downto 0):=(others=>'0')"
        )
        architecture.architecture_declaration_list.append(
            "signal h_config_addr:std_logic_vector(HIDDEN_ADDR_WIDTH-1 downto 0) :=(others=>'0')"
        )
        architecture.architecture_declaration_list.append(
            "signal c_config_en: std_logic:='0'"
        )
        architecture.architecture_declaration_list.append(
            "signal c_config_data:std_logic_vector(DATA_WIDTH-1 downto 0):=(others=>'0')"
        )
        architecture.architecture_declaration_list.append(
            "signal c_config_addr:std_logic_vector(HIDDEN_ADDR_WIDTH-1 downto 0) :=(others=>'0')"
        )
        architecture.architecture_declaration_list.append(
            "signal done :  std_logic:='0'"
        )
        architecture.architecture_declaration_list.append("signal h_out_en : std_logic")
        architecture.architecture_declaration_list.append(
            "signal h_out_addr : std_logic_vector(HIDDEN_ADDR_WIDTH-1 downto 0) :=(others=>'0')"
        )
        architecture.architecture_declaration_list.append(
            "signal h_out_data : std_logic_vector(DATA_WIDTH-1 downto 0):=(others=>'0')"
        )
        architecture.architecture_declaration_list.append(
            "type X_H_ARRAY is array (0 to 31) of signed(16-1 downto 0)"
        )
        architecture.architecture_declaration_list.append(
            "type C_ARRAY is array (0 to 31) of signed(16-1 downto 0)"
        )
        architecture.architecture_declaration_list.append(
            f"signal test_x_h_data : X_H_ARRAY := ({form_to_hex_list(self.test_x_h_data)})"
        )
        architecture.architecture_declaration_list.append(
            f"signal test_c_data : C_ARRAY := ({form_to_hex_list(self.test_c_data)})"
        )
        architecture.architecture_component_list.append(procedure_0)
        architecture.architecture_component_list.append(procedure_1)
        architecture.architecture_process_list.append(process)
        architecture.architecture_port_map_list.append(uut_port_map)
        architecture.architecture_assignment_at_end_of_declaration_list.append(
            "clk <= clock"
        )
        architecture.architecture_statement_part = test_process

        code = chain(chain(library(), entity()), architecture())
        return code