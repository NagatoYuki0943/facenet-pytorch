#---------------------------------------------------#
#   MobileNetV1
#---------------------------------------------------#

import torch.nn as nn

#---------------------------------------------------#
#   Conv+BN+ReLU6
#---------------------------------------------------#
def conv_bn(inp, oup, stride = 1):
    return nn.Sequential(
        nn.Conv2d(inp, oup, 3, stride, 1, bias=False),
        nn.BatchNorm2d(oup),
        nn.ReLU6()
    )

#---------------------------------------------------#
#   dw+pw
#   3x3DWConv + 1x1Conv
#---------------------------------------------------#
def conv_dw(inp, oup, stride = 1):
    return nn.Sequential(
        # 3x3Conv
        # in = put = groups
        nn.Conv2d(inp, inp, 3, stride, 1, groups=inp, bias=False),
        nn.BatchNorm2d(inp),
        nn.ReLU6(),

        # 1x1Conv
        nn.Conv2d(inp, oup, 1, 1, 0, bias=False),
        nn.BatchNorm2d(oup),
        nn.ReLU6(),
    )

#---------------------------------------------------#
#   MobileNetV1
#---------------------------------------------------#
class MobileNetV1(nn.Module):
    def __init__(self):
        super(MobileNetV1, self).__init__()
        self.stage1 = nn.Sequential(
            # 160,160,3 -> 80,80,32
            conv_bn(3, 32, 2), 
            # 80,80,32 -> 80,80,64
            conv_dw(32, 64, 1), 

            # 80,80,64 -> 40,40,128
            conv_dw(64, 128, 2),
            conv_dw(128, 128, 1),

            # 40,40,128 -> 20,20,256
            conv_dw(128, 256, 2),
            conv_dw(256, 256, 1),
        )
        # 20,20,256 -> 10,10,512
        self.stage2 = nn.Sequential(
            conv_dw(256, 512, 2),
            conv_dw(512, 512, 1),
            conv_dw(512, 512, 1),
            conv_dw(512, 512, 1),
            conv_dw(512, 512, 1),
            conv_dw(512, 512, 1),
        )

        # 10,10,512 -> 5,5,1024
        self.stage3 = nn.Sequential(
            conv_dw(512, 1024, 2),
            conv_dw(1024, 1024, 1),
        )

        self.avg = nn.AdaptiveAvgPool2d((1,1))
        self.fc = nn.Linear(1024, 1000)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.normal_(m.weight, 0, 0.1)
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
    def forward(self, x):
        x = self.stage1(x)  # 160,160,3 -> 20,20,256
        x = self.stage2(x)  # 20,20,256 -> 10,10,512
        x = self.stage3(x)  # 10,10,512 -> 5,5, 1024
        x = self.avg(x)
        # x = self.model(x)
        x = x.view(-1, 1024)
        x = self.fc(x)
        return x
