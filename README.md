# ElasticAi.creator

Design, train and compile neural networks optimized specifically for FPGAs.
Obtaining a final model is typically a three stage process.
* design and train it using the layers provided in the `elasticai.creator.qat` package.
* translate the model to a target representation, e.g. VHDL
* compile the intermediate representation with a third party tool, e.g. Xilinx Vivado (TM)

This version currently only supports parts of VHDL as target representations.

The project is part of the elastic ai ecosystem developed by the Embedded Systems Department of the University Duisburg-Essen. For more details checkout the slides at [researchgate](https://www.researchgate.net/publication/356372207_In-Situ_Artificial_Intelligence_for_Self-_Devices_The_Elastic_AI_Ecosystem_Tutorial).


## Table of contents

- [Users Guide](#users-guide)
  - [Install](#install)
- [Structure of the Project](#structure-of-the-project)
- [General Limitations](#general-limitations)
- [Developers Guide](#developers-guide)
  - [Install Dev Dependencies](#install-dev-dependencies)


## Users Guide

### Install
You can install the ElasticAI.creator as a dependency using pip:
```bash
python3 -m pip install "elasticai.creator"
```


## Structure of the Project

The structure of the project is as follows.
The [creator](elasticai/creator) folder includes all main concepts of our project, especially the qtorch implementation which is our implementation of quantized PyTorch layer.
It also includes the supported target representations, like the subfolder [vhdl](elasticai/creator/vhdl) is for the translation to vhdl.
Additionally, we have folders for [unit tests](elasticai/creator/tests) and [integration tests](elasticai/creator/integrationTests).

### Structure of the translator

The actual translator, which can translate a model into a VHDL implementation, can be found in the package
`elasticai.creator.vhdl.translator`. An implementation for translating PyTorch models to VHDL can be found in the module
`elasticai.creator.vhdl.translator.pytorch.translator`.

#### Translation with the help of templates

To translate a particular component into VHDL, we use templates. A template is a VHDL text file which contains
placeholders, which are filled with values by a so-called `VHDLComponent` class. A `VHDLComponent` class is
a class that contains a filename of the VHDL file and returns the code without placeholders when the object is called.
For each component we create an implementation of the `VHDLComponent` protocol that replaces the placeholders.
An incomplete class diagram illustrating this is the following:

```mermaid
classDiagram
class VHDLComponent {
    <<interface>>
    +String file_name
    +__call__() Code
}
VHDLModule "1" o-- "1..*" VHDLComponent
VHDLComponent <|.. VHDLStaticComponent
VHDLComponent <|.. SigmoidComponent
VHDLComponent <|.. TanhComponent
VHDLComponent <|.. RomComponent
VHDLComponent <|.. Linear1dComponent
VHDLStaticComponent <|-- LSTMComponent
VHDLStaticComponent <|-- LSTMCommonComponent
VHDLStaticComponent <|-- DualPort2ClockRamComponent
```

Static VHDL files that have no placeholders are represented by a `VHDLStaticComponent`.

A layer (e.g. an LSTM layer) can consist of more than one VHDLComponent. For this reason we call a
`Iterable[VHDLComponent]` a `VHDLModule`.

#### Translatables

In order to represent a layer independently of the machine learning framework used, every layer that needs to be
translated is represented as translatable. A `Translatable` class has a `translate` function that takes a
DTO (Data Transfer Object) which contains all necessary parameters from the user to translate the layer to VHDL and
returns a `VHDLModule` as the result of the translation.

An incomplete class diagram showing this for the `LSTMTranslatable` and `Linear1dTranslatable` is the following:

```mermaid
classDiagram
class Translatable {
    <<interface>>
    +translate(Any args) VHDLModule
}

class LSTMTranslatable {
    +weights_ih
    +weights_hh
    +biases_ih
    +biases_hh
    +translate(LSTMTranslationArgs args) VHDLModule
}
class LSTMTranslationArgs {
    +fixed_point_factory
    +sigmoid_resolution
    +tanh_resolution
}

class Linear1dTranslatable {
    +weight
    +bias
    +translate(Linear1dTranslationArgs args) VHDLModule
}
class Linear1dTranslationArgs {
    +fixed_point_factory
}

Translatable <|.. LSTMTranslatable
LSTMTranslatable -- LSTMTranslationArgs
Translatable <|.. Linear1dTranslatable
Linear1dTranslatable -- Linear1dTranslationArgs
```

#### Build Functions

To convert a layer from a particular machine learning framework to the corresponding translatable, we use build
functions for each layer of the machine learning framework. A build function is a function that takes the current layer
object of the machine learning framework and returns a `Translatable` object. In this build function, all the
necessary parameters of the layer are extracted and these parameters are used to create the corresponding translatable
object. To translate a model of a machine learning framework, there is a `BuildFunctionMapping` that maps all supported
layers to their corresponding build function.

We already provide a predefined `BuildFunctionMapping` instance that translates each layer in a typical way
(`elasticai.creator.vhdl.translator.pytorch.build_function_mappings.DEFAULT_BUILD_FUNCTION_MAPPING`).

#### Translation process
In the following diagram you can see the typical process of translating a given PyTorch model into VHDL files using
the functions `translate_model`, `generate_code` and `save_code` which can be found in the module
`elasticai.creator.vhdl.translator.pytorch.translator`:

```mermaid
flowchart TD
start([Start]) ---> translate_model
translate_model ---> |"Iterator[Translatable]"| generate_code
generate_code ---> |"Iterator[CodeModule]"| save_code
save_code ---> stop([Stop])
model[/Model/] -.- translate_model
build_function_mapping[[BuildFunctionMapping]] <-.-> |Request BuildFunctions| translate_model
translation_args[/Translation arguments for each Translatable/] -.- generate_code
save_code -.-> saved_data[/Saved VHDL files/]
```


## General Limitations

By now we only support Sequential models for our translations.

## Developers Guide
### Install Dev Dependencies
- [poetry](https://python-poetry.org/)
- recommended:
  - [pre-commit](https://pre-commit.com/)
  - [commitlint](https://github.com/conventional-changelog/commitlint) to help following our [conventional commit](https://www.conventionalcommits.org/en/v1.0.0-beta.2/#summary) guidelines
poetry can be installed in the following way:
```bash
pip install poetry
poetry install
poetry shell
pre-commit install
npm install --save-dev @commitlint/{config-conventional,cli}
sudo apt install ghdl
```

### Commit Message Scopes

- **qat**: quantization-aware-training
  - Examples: `QConv1D`, `QLSTM`, autograd functions, etc.
- **readme**
- **precomputation**: entities that deal with the precomputation of ML components
  - Examples: the `precomputable` decorator or the `IOTable` class
- **vhdl**: vhdl code generation
  - Examples: `vhdl.TruthTable`, `vhdl.LSTMCell`
- **gh-workflow**
- **pyproject**: changes to the `pyproject.toml` file will typically either update run or dev dependencies
- **typing**: changing type annotations and changes to code to allow consistent type annotations
- **pre-commit**

### Adding new translation targets
New translation targets should be located in their own folder, e.g. vhdl for translating from any language to vhdl.
Workflow for adding a new translation:
1. Obtain a structure, such as a list in a sequential case, which will describe the connection between every component.
2. Identify and label relevant structures, in the base cases it can be simply separate layers.
3. Map each structure to its function which will convert it.
4. Do such conversions.
5. Recreate connections based on 1.

Each sub-step should be separable and it helps for testing if common functions are wrapped around an adapter.

### Syntax Checking

[GHDL](https://ghdl.github.io/ghdl/) supports a [syntax checking](https://umarcor.github.io/ghdl/using/InvokingGHDL.html#check-syntax-s) which checks the syntax of a vhdl file without generating code.
The command is as follows:
```
ghdl -s path/to/vhdl/file
```
So, for example for checking the sigmoid source vhdl files in our project we can run:
```
ghdl -s elasticai/creator/vhdl/source/sigmoid.vhd
```
For checking all vhdl files together in our project we can just run:
```
ghdl -s elasticai/creator/**/*.vhd
```

### Tests

Our implementation is fully tested with unit, integration and system tests.
Please refer to the system tests as examples of how to use the Elastic Ai Creator Translator.
You can run one explicit test with the following statement:

```python -m unittest discover -p "test_*.py" elasticai/creator/path/to/test.py```

If you want to run all tests, give the path to the tests:

```python -m unittest discover -p "test_*.py" elasticai/creator/path/to/testfolder```

You can also run all tests together:

```python -m unittest discover -p "test_*.py" elasticai/creator/translator/path/to/language/```

If you want to add more tests please refer to the Test Guidelines in the following.

### Test style Guidelines

#### File IO
In general try to avoid interaction with the filesystem. In most cases instead of writing to or reading from a file you can use a StringIO object or a StringReader.
If you absolutely have to create files, be sure to use pythons [tempfile](https://docs.python.org/3.9/library/tempfile.html) module and cleanup after the tests.


#### Diectory structure and file names
Files containing tests for a python module should be located in a test directory for the sake of separation of concerns.
Each file in the test directory should contain tests for one and only one class/function defined in the module.
Files containing tests should be named according to the rubric
`test_ClassName.py`.
Next, if needed for more specific tests define a class. Then subclass it, in this class define a setUp method (and possibly tearDown) to create the global environment.
It avoids introducing the category of bugs associated with copying and pasting code for reuse.
This class should be named similarly to the file name.
There's a category of bugs that appear if  the initialization parameters defined at the top of the test file are directly used: some tests require the initialization parameters to be changed slightly.
Its possible to define a parameter and have it change in memory as a result of a test.
Subsequent tests will therefore throw errors.
Each class contains methods that implement a test.
These methods are named according to the rubric
`test_name_condition`

#### Unit tests
In those tests each functionality of each function in the module is tested, it is the entry point  when adding new functions.
It assures that the function behaves correctly independently of others.
Each test has to be fast, so use of heavier libraries is discouraged.
The input used is the minimal one needed to obtain a reproducible output.
Dependencies should be replaced with mocks as needed.

#### Integration Tests
Here the functions' behaviour with other modules is tested.
In this repository each integration function is in the correspondent folder.
Then the integration with a single class of the target, or the minimum amount of classes for a functionality, is tested in each separated file.

#### System tests
Those tests will use every component of the system, comprising multiple classes.
Those tests include expected use cases and unexpected or stress tests.

#### Adding new functionalities and tests required
When adding new functions to an existing module, add unit tests in the correspondent file in the same order of the module, if a new module is created a new file should be created.
When a bug is solved created the respective regression test to ensure that it will not return.
Proceed similarly with integration tests.
Creating a new file if a functionality completely different from the others is created e.g. support for a new layer.
System tests are added if support for a new library is added.

#### Updating tests
If new functionalities are changed or removed the tests are expected to reflect that, generally the ordering is unit tests -> integration tests-> system tests.
Also, unit tests that change the dependencies should be checked, since this system is fairly small the internal dependencies are not always mocked.

references: https://jrsmith3.github.io/python-testing-style-guidelines.html
