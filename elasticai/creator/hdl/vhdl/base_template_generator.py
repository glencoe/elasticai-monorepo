from elasticai.creator.hdl.code_generation.abstract_base_template import (
    TemplateConfig,
    TemplateExpander,
    module_to_package,
)

"""
We want to programmatically use designs that are either hand-written or based on hand-written templates
these designs need to adhere to a well defined protocol. As a hardware designer you specify your protocol
and the expected version of the elasticai.creator in a file called `design_meta.toml` that lives in the
same folder as your `layer.py` that defines how the hdl code for the hardware design and the behaviour of
the corresponding neural network layer in software.

To help you as hardware designer stick to specific protocol you can generate a base template, that you
can use as a starting point to develop your design.
"""


class BaseTemplateGenerator:
    def __init__(self):
        self._base_config = TemplateConfig(
            package=module_to_package(self.__module__),
            file_name="base_template.tpl.vhd",
            parameters={},
        )

    def generate(self) -> str:
        return self._expand_base_template()

    def _expand_base_template(self) -> str:
        return "\n".join(TemplateExpander(self._base_config).lines())