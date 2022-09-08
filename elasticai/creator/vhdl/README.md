# Structure of the translator

The actual translator, which can translate a model into a VHDL implementation, can be found in the package
`elasticai.creator.vhdl.translator`. An implementation for translating PyTorch models to VHDL can be found in the module
`elasticai.creator.vhdl.translator.pytorch.translator`.

## Translation with the help of templates

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
VHDLComponent <|-- LSTMComponent
VHDLStaticComponent <|-- LSTMCommonComponent
VHDLStaticComponent <|-- DualPort2ClockRamComponent
```

Static VHDL files that have no placeholders are represented by a `VHDLStaticComponent`.

A layer (e.g. an LSTM layer) can consist of more than one VHDLComponent. For this reason we call a
`Iterable[VHDLComponent]` a `VHDLModule`.

## Translatables

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
    +work_library_name
}

class Linear1dTranslatable {
    +weight
    +bias
    +translate(Linear1dTranslationArgs args) VHDLModule
}
class Linear1dTranslationArgs {
    +fixed_point_factory
    +work_library_name
}

Translatable <|.. LSTMTranslatable
LSTMTranslatable -- LSTMTranslationArgs
Translatable <|.. Linear1dTranslatable
Linear1dTranslatable -- Linear1dTranslationArgs
```

## Build Functions

To convert a layer from a particular machine learning framework to the corresponding translatable, we use build
functions for each layer of the machine learning framework. A build function is a function that takes the current layer
object of the machine learning framework and returns a `Translatable` object. In this build function, all the
necessary parameters of the layer are extracted and these parameters are used to create the corresponding translatable
object. To translate a model of a machine learning framework, there is a `BuildFunctionMapping` that maps all supported
layers to their corresponding build function.

We already provide a predefined `BuildFunctionMapping` instance that translates each layer in a typical way
(`elasticai.creator.vhdl.translator.pytorch.build_function_mappings.DEFAULT_BUILD_FUNCTION_MAPPING`).

## Translation process
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