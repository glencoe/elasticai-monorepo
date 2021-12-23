from functools import partial
from io import StringIO

from torch.nn import Sequential, MaxPool1d, Conv1d

from elasticai.creator.input_domains import (
    create_input_for_1d_conv,
    create_depthwise_input_for_1d_conv,
)
from elasticai.creator.layers import QConv1d, Binarize
from elasticai.creator.precomputation import (
    precomputable,
    get_precomputations_from_direct_children,
)

model = Sequential(
    QConv1d(
        in_channels=2,
        out_channels=2,
        kernel_size=(3,),
        quantizer=Binarize(),
    ),
    MaxPool1d(kernel_size=2),
    Binarize(),
    precomputable(
        Sequential(
            Conv1d(
                in_channels=2,
                out_channels=2,
                kernel_size=(4,),
                groups=2,
            ),
            Binarize(),
        ),
        input_generator=partial(
            create_depthwise_input_for_1d_conv, shape=(2, 4), items=[-1, 1]
        ),
        input_shape=(2, 2),
    ),
    MaxPool1d(kernel_size=2),
    precomputable(
        Sequential(
            Conv1d(
                in_channels=2,
                out_channels=3,
                kernel_size=(1,),
            ),
            Binarize(),
        ),
        input_generator=partial(create_input_for_1d_conv, shape=(1, 2), items=[-1, 1]),
        input_shape=(6, 1),
    ),
)

model.eval()

with StringIO() as f:
    for precompute in get_precomputations_from_direct_children(model):
        precompute()
        precompute.dump_to(f)
    print(f.getvalue())
