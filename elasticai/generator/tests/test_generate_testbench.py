import unittest
from elasticai.generator.generate_testbench import write_libraries, write_entity, write_architecture_header, \
    write_component, write_signal_definitions, write_type_definitions, write_variable_definition, \
    write_clock_process, write_uut, write_test_process_header, write_test_process_end, write_architecture_end


class GenerateTestBenchTest(unittest.TestCase):
    def test_generate_libraries(self) -> None:
        expected_import_lines = [
            "library ieee;",
            "use ieee.std_logic_1164.all;",
            "use ieee.numeric_std.all;               -- for type conversions"
        ]
        lib_string = write_libraries()
        for i in range(0, 3):
            self.assertEqual(expected_import_lines[i], lib_string.splitlines()[i])

    def test_generate_libraries_with_math_lib(self) -> None:
        expected_import_lines = [
            "library ieee;",
            "use ieee.std_logic_1164.all;",
            "use ieee.numeric_std.all;               -- for type conversions",
            "use ieee.math_real.all;                 -- for the ceiling and log constant calculation function"
        ]
        lib_string = write_libraries(math_lib=True)
        for i in range(0, 4):
            self.assertEqual(expected_import_lines[i], lib_string.splitlines()[i])

    def test_generate_entity_with_generic_without_vector_length_width(self) -> None:
        expected_entity_lines = [
            "entity sigmoid_tb is",
            "    generic (",
            "        DATA_WIDTH : integer := 16;",
            "        FRAC_WIDTH : integer := 8",
            "        );",
            "    port ( clk: out std_logic);",
            "end entity ; -- sigmoid_tb"
        ]
        entity_string = write_entity(entity_name="sigmoid", data_width=16, frac_width=8)
        for i in range(len(expected_entity_lines)):
            self.assertEqual(expected_entity_lines[i], entity_string.splitlines()[i])

    def test_generate_entity_with_generic(self) -> None:
        expected_entity_lines = [
            "entity lstm_common_gate_tb is",
            "    generic (",
            "        DATA_WIDTH : integer := 16;",
            "        FRAC_WIDTH : integer := 8;",
            "        VECTOR_LEN_WIDTH : integer := 4",
            "        );",
            "    port ( clk: out std_logic);",
            "end entity ; -- lstm_common_gate_tb",
        ]
        entity_string = write_entity(entity_name="lstm_common_gate", data_width=16, frac_width=8, vector_len_width=4)
        for i in range(len(expected_entity_lines)):
            self.assertEqual(expected_entity_lines[i], entity_string.splitlines()[i])

    def test_generate_architecture_header(self) -> None:
        expected_architecture_header_line = "architecture behav of sigmoid_tb is"
        architecture_header_string = write_architecture_header(architecture_name="behav", component_name="sigmoid")
        self.assertEqual(expected_architecture_header_line, architecture_header_string.splitlines()[0])

    def test_generate_component(self) -> None:
        expected_component_lines = [
            "    ------------------------------------------------------------",
            "    -- Declare Components for testing",
            "    ------------------------------------------------------------",
            "    component sigmoid is",
            "        generic (",
            "                DATA_WIDTH : integer := 16;",
            "                FRAC_WIDTH : integer := 8",
            "            );",
            "        port (",
            "            x : in signed(DATA_WIDTH-1 downto 0);",
            "            y : out signed(DATA_WIDTH-1 downto 0)",
            "        );",
            "    end component sigmoid;"
        ]
        component_string = write_component(component_name="sigmoid", data_width=16, frac_width=8, variables_dict={
            "x": "in signed(DATA_WIDTH-1 downto 0)",
            "y": "out signed(DATA_WIDTH-1 downto 0)"})
        for i in range(len(expected_component_lines)):
            self.assertEqual(expected_component_lines[i], component_string.splitlines()[i])

    def test_generate_component_with_different_in_and_out_variables(self) -> None:
        expected_component_lines = [
            "    ------------------------------------------------------------",
            "    -- Declare Components for testing",
            "    ------------------------------------------------------------",
            "    component lstm_common_gate is",
            "        generic (",
            "                DATA_WIDTH : integer := 16;",
            "                FRAC_WIDTH : integer := 8;",
            "                VECTOR_LEN_WIDTH : integer := 4",
            "            );",
            "        port (",
            "            reset : in std_logic;",
            "            clk : in std_logic;",
            "            x : in signed(DATA_WIDTH-1 downto 0);",
            "            w : in signed(DATA_WIDTH-1 downto 0);",
            "            b : in signed(DATA_WIDTH-1 downto 0);",
            "            vector_len : in unsigned(VECTOR_LEN_WIDTH-1 downto 0);",
            "            idx : out unsigned(VECTOR_LEN_WIDTH-1 downto 0);",
            "            ready : out std_logic;",
            "            y : out signed(DATA_WIDTH-1 downto 0)",
            "        );",
            "    end component lstm_common_gate;"
        ]
        component_string = write_component(component_name="lstm_common_gate", data_width=16, frac_width=8,
                                           variables_dict={
                                               "reset": "in std_logic",
                                               "clk": "in std_logic",
                                               "x": "in signed(DATA_WIDTH-1 downto 0)",
                                               "w": "in signed(DATA_WIDTH-1 downto 0)",
                                               "b": "in signed(DATA_WIDTH-1 downto 0)",
                                               "vector_len": "in unsigned(VECTOR_LEN_WIDTH-1 downto 0)",
                                               "idx": "out unsigned(VECTOR_LEN_WIDTH-1 downto 0)",
                                               "ready": "out std_logic",
                                               "y": "out signed(DATA_WIDTH-1 downto 0)"
                                           }, vector_len_width=4)
        for i in range(len(expected_component_lines)):
            self.assertEqual(expected_component_lines[i], component_string.splitlines()[i])

    def test_generate_signal_definitions(self) -> None:
        expected_inputs_lines = [
            "    ------------------------------------------------------------",
            "    -- Testbench Internal Signals",
            "    ------------------------------------------------------------",
            "    signal clk_period : time := 1 ns;",
            "    signal test_input : signed(16-1 downto 0):=(others=>'0');",
            "    signal test_output : signed(16-1 downto 0);"
        ]
        signal_definition_string = write_signal_definitions(signal_dict={
            "clk_period": "time := 1 ns",
            "test_input": "signed(16-1 downto 0):=(others=>'0')",
            "test_output": "signed(16-1 downto 0)"
        })
        for i in range(len(expected_inputs_lines)):
            self.assertEqual(expected_inputs_lines[i], signal_definition_string.splitlines()[i])

    def test_generate_signal_definitions_multiple(self) -> None:
        expected_inputs_lines = [
            "    ------------------------------------------------------------",
            "    -- Testbench Internal Signals",
            "    ------------------------------------------------------------",
            "    signal clk_period : time := 2 ps;",
            "    signal clock : std_logic;",
            "    signal reset, ready : std_logic:='0';",
            "    signal X_MEM : RAM_ARRAY :=(others=>(others=>'0'));",
            "    signal W_MEM : RAM_ARRAY:=(others=>(others=>'0'));",
            "    signal x, w, y, b : signed(DATA_WIDTH-1 downto 0):=(others=>'0');",
            "    signal vector_len : unsigned(VECTOR_LEN_WIDTH-1 downto 0):=(others=>'0');",
            "    signal idx : unsigned(VECTOR_LEN_WIDTH-1 downto 0):=(others=>'0');",
        ]
        signal_definition_string = write_signal_definitions(signal_dict={
            "clk_period": "time := 2 ps",
            "clock": "std_logic",
            "reset, ready": "std_logic:='0'",
            "X_MEM": "RAM_ARRAY :=(others=>(others=>'0'))",
            "W_MEM": "RAM_ARRAY:=(others=>(others=>'0'))",
            "x, w, y, b": "signed(DATA_WIDTH-1 downto 0):=(others=>'0')",
            "vector_len": "unsigned(VECTOR_LEN_WIDTH-1 downto 0):=(others=>'0')",
            "idx": "unsigned(VECTOR_LEN_WIDTH-1 downto 0):=(others=>'0')",
        })
        for i in range(len(expected_inputs_lines)):
            self.assertEqual(expected_inputs_lines[i], signal_definition_string.splitlines()[i])

    def test_generate_type_definition(self) -> None:
        expected_inputs_lines = [
            "    ------------------------------------------------------------",
            "    -- Testbench Data Type",
            "    ------------------------------------------------------------",
            "    type RAM_ARRAY is array (0 to 9 ) of signed(DATA_WIDTH-1 downto 0);",
        ]
        type_definition_string = write_type_definitions(type_dict={
            "RAM_ARRAY": "array (0 to 9 ) of signed(DATA_WIDTH-1 downto 0)",
        })
        for i in range(len(expected_inputs_lines)):
            self.assertEqual(expected_inputs_lines[i], type_definition_string.splitlines()[i])

    def test_generate_variable_definition(self) -> None:
        expected_variable_lines = [
           "    clk <= clock;"
        ]
        variable_definition_string = write_variable_definition(variable_dict={
            "clk": "clock",
        })
        for i in range(len(expected_variable_lines)):
            self.assertEqual(expected_variable_lines[i], variable_definition_string.splitlines()[i])

    def test_generate_clock_process(self) -> None:
        expected_clock_lines = [
            "    clock_process : process",
            "    begin",
            "        clk <= '0';",
            "        wait for clk_period/2;",
            "        clk <= '1';",
            "        wait for clk_period/2;",
            "    end process; -- clock_process"
        ]
        clock_process_string = write_clock_process()
        for i in range(len(expected_clock_lines)):
            self.assertEqual(expected_clock_lines[i], clock_process_string.splitlines()[i])

    def test_generate_uut(self) -> None:
        expected_uut_lines = [
            "    uut: sigmoid",
            "    port map (",
            "        x => test_input,",
            "        y => test_output",
            "    );"
        ]
        utt_string = write_uut(component_name="sigmoid", mapping_dict={"x": "test_input", "y": "test_output"})
        for i in range(len(expected_uut_lines)):
            self.assertEqual(expected_uut_lines[i], utt_string.splitlines()[i])

    def test_generate_bigger_uut(self) -> None:
        expected_uut_lines = [
            "    uut: lstm_common_gate",
            "    port map (",
            "        reset => reset,",
            "        clk => clock,",
            "        x => x,",
            "        w => w,",
            "        b => b,",
            "        vector_len => vector_len,",
            "        idx => idx,",
            "        ready => ready,",
            "        y => y",
            "    );"
        ]
        utt_string = write_uut(component_name="lstm_common_gate",
                               mapping_dict={
                                   "reset": "reset",
                                   "clk": "clock",
                                   "x": "x",
                                   "w": "w",
                                   "b": "b",
                                   "vector_len": "vector_len",
                                   "idx": "idx",
                                   "ready": "ready",
                                   "y": "y"
                               })
        for i in range(len(expected_uut_lines)):
            self.assertEqual(expected_uut_lines[i], utt_string.splitlines()[i])

    def test_generate_test_process_header(self) -> None:
        expected_test_process_header_lines = [
            "    test_process: process is",
            "    begin",
            "        Report \"======Simulation start======\" severity Note;",
        ]
        test_process_header_string = write_test_process_header()
        for i in range(len(expected_test_process_header_lines)):
            self.assertEqual(expected_test_process_header_lines[i], test_process_header_string.splitlines()[i])

    def test_generate_test_process_end(self) -> None:
        expected_test_process_end_lines = [
            "",
            "        -- if there is no error message, that means all test case are passed.",
            "        report \"======Simulation Success======\" severity Note;",
            "        report \"Please check the output message.\" severity Note;",
            "",
            "        -- wait forever",
            "        wait;",
            "",
            "    end process; -- test_process",
        ]
        test_process_end_string = write_test_process_end()
        for i in range(len(expected_test_process_end_lines)):
            self.assertEqual(expected_test_process_end_lines[i], test_process_end_string.splitlines()[i])

    def test_generate_architecture_end(self) -> None:
        expected_test_architecture_end_line = "end behav ; -- behav"
        architecture_end_string = write_architecture_end(architecture_name="behav")
        self.assertEqual(expected_test_architecture_end_line, architecture_end_string.splitlines()[0])
