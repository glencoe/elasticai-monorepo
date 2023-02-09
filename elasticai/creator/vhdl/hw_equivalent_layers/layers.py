import typing
from typing import Any

import torch.nn

import elasticai.creator.mlframework
from elasticai.creator.mlframework import Module
from elasticai.creator.nn.hard_sigmoid import HardSigmoid as nnHardSigmoid
from elasticai.creator.nn.linear import FixedPointLinear as nnFixedPointLinear
from elasticai.creator.vhdl.code import CodeModule, CodeModuleBase
from elasticai.creator.vhdl.code_files.utils import calculate_address_width
from elasticai.creator.vhdl.designs.network_blocks import (
    BufferedNetworkBlock,
    NetworkBlock,
)
from elasticai.creator.vhdl.designs.vhdl_files import VHDLFile
from elasticai.creator.vhdl.number_representations import FixedPointConfig
from elasticai.creator.vhdl.tracing.hw_equivalent_fx_tracer import HWEquivalentFXTracer
from elasticai.creator.vhdl.tracing.typing import (
    HWEquivalentGraph,
    HWEquivalentTracer,
    TranslatableLayer,
)


class RootModule(torch.nn.Module, elasticai.creator.mlframework.Module):
    def __init__(self):
        self.elasticai_tags = {
            "x_address_width": 1,
            "y_address_width": 1,
            "x_width": 1,
            "y_width": 1,
        }
        torch.nn.Module.__init__(self)

    def _template_parameters(self) -> dict[str, str]:
        return dict(((key, str(value)) for key, value in self.elasticai_tags.items()))

    def _get_tracer(self) -> HWEquivalentTracer:
        return HWEquivalentFXTracer()

    def translate(self) -> CodeModule:
        module: Module = typing.cast(Module, self)
        graph = self._get_tracer().trace(module)

        def generate_port_maps(graph: HWEquivalentGraph[TranslatableLayer]):
            port_maps = []
            for node in graph.hw_equivalent_nodes:
                module = graph.get_module_for_node(node)
                design = module.translate()
                port_map = design.get_port_map(node.name)
                port_maps.append(port_map)

            return port_maps

        port_maps = generate_port_maps(graph)
        signals = [line for m in port_maps for line in m.signal_definitions()]
        layer_instantiations = [line for m in port_maps for line in m.code()]
        layer_connections = ["fp_linear_x <= x;"]
        file = VHDLFile(
            template_name="network",
            signals=signals,
            layer_instantiations=layer_instantiations,
            layer_connections=layer_connections,
        )
        file.update_parameters(**self._template_parameters())
        file.update_parameters(signal_definitions=signals)
        design = CodeModuleBase(name="network", files=(file,))
        return design


class FixedPointHardSigmoid(nnHardSigmoid):
    def __init__(
        self,
        fixed_point_factory: FixedPointConfig,
        in_place: bool = False,
        *,
        data_width,
    ):
        super().__init__(fixed_point_factory, in_place)
        self._hw_block = NetworkBlock("", "", x_width=data_width, y_width=data_width)

    def translate(self):
        return self._hw_block

class FixedPointLinear(nnFixedPointLinear):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        fixed_point_factory: FixedPointConfig,
        bias: bool = True,
        device: Any = None,
        *,
        data_width: int,
    ):
        super().__init__(
            in_features=in_features,
            out_features=out_features,
            fixed_point_factory=fixed_point_factory,
            bias=bias,
            device=device,
        )
        self._hw_block = BufferedNetworkBlock(
            name="fp_linear",
            template_name="",
            y_width=data_width,
            x_width=data_width,
            x_address_width=calculate_address_width(in_features),
            y_address_width=calculate_address_width(out_features),
        )

    def translate(self):
        return self._hw_block
