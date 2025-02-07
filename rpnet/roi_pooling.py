import torch
import torch.autograd as ag
from torch.autograd.function import Function


class AdaptiveMaxPool2d(torch.nn.Module):
    def __init__(self, out_w, out_h):
        super().__init__()
        self.out_w = out_w
        self.out_h = out_h
        self.m = torch.nn.AdaptiveMaxPool2d([out_h, out_w])

    def forward(self, input):
        return self.m(input)


def adaptive_max_pool(input, size):
    return AdaptiveMaxPool2d(size[0], size[1])(input)


def roi_pooling(input, rois, size=(7, 7), spatial_scale=1.0):
    assert (rois.dim() == 2)
    assert (rois.size(1) == 5)
    output = []
    rois = rois.data.float()
    num_rois = rois.size(0)

    rois[:, 1:].mul_(spatial_scale)
    rois = rois.long()
    for i in range(num_rois):
        roi = rois[i]
        im_idx = roi[0]
        # im = input.narrow(0, im_idx, 1)
        im = input.narrow(0, im_idx, 1)[..., roi[2]:(roi[4] + 1), roi[1]:(roi[3] + 1)]
        output.append(adaptive_max_pool(im, size))

    return torch.cat(output, 0)


def roi_pooling_ims(input, rois, size=(7, 7), spatial_scale=1.0):
    # written for one roi one image
    # size: (w, h)
    assert (rois.dim() == 2)
    assert len(input) == len(rois)
    assert (rois.size(1) == 4)
    output = []
    rois = rois.data.float()
    num_rois = rois.size(0)

    rois[:, 1:].mul_(spatial_scale)
    rois = rois.long()
    for i in range(num_rois):
        roi = rois[i]
        # im = input.narrow(0, im_idx, 1)
        im = input.narrow(0, i, 1)[..., roi[1]:(roi[3] + 1), roi[0]:(roi[2] + 1)]
        output.append(adaptive_max_pool(im, size))

    return torch.cat(output, 0)

if __name__ == '__main__':
    input = ag.Variable(torch.rand(2, 1, 10, 10), requires_grad=True)
    rois = ag.Variable(torch.LongTensor([[1, 2, 7, 8], [3, 3, 8, 8]]), requires_grad=False)

    out = roi_pooling_ims(input, rois, size=(8, 8))
    out.backward(out.data.clone().uniform_())

    # input = ag.Variable(torch.rand(2, 1, 10, 10), requires_grad=True)
    # rois = ag.Variable(torch.LongTensor([[0, 1, 2, 7, 8], [0, 3, 3, 8, 8], [1, 3, 3, 8, 8]]), requires_grad=False)
    # rois = ag.Variable(torch.LongTensor([[0,3,3,8,8]]),requires_grad=False)

    # out = adaptive_max_pool(input, (3, 3))
    # out.backward(out.data.clone().uniform_())

    # out = roi_pooling(input, rois, size=(3, 3))
    # out.backward(out.data.clone().uniform_())
