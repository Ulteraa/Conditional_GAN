import torch
import torch.nn as nn
class Critic(nn.Module):

    def __init__(self, in_channel,depth_scaling,image_size,num_class):
        super(Critic, self).__init__()
        self.image_size=image_size
        self.dis = nn.Sequential(nn.Conv2d(in_channel+1, depth_scaling, 4, 2, 1),# _,32*32
                               nn.LeakyReLU(0.2),
                               self._block(depth_scaling, 2*depth_scaling), # 16*16
                               self._block(2*depth_scaling, 4 * depth_scaling), #8*8
                               self._block(4*depth_scaling, 8 * depth_scaling),# 4*4
                               nn.Conv2d(8 * depth_scaling, 1, 4, 2, 0), # 1*1
                               )
        self.embeding = nn.Embedding(num_class,image_size*image_size)

    def _block(self,in_chanel, out_chanel):
            return nn.Sequential(nn.Conv2d(in_chanel, out_chanel,4,2,1,bias=False),
                          nn.InstanceNorm2d(out_chanel, affine=True),
                          nn.LeakyReLU(0.1))
    def forward(self,x,lable):
        embed=self.embeding(lable).reshape(lable.shape[0], 1, self.image_size, self.image_size)
        x=torch.cat([x, embed], dim=1)
        return self.dis(x)

class Generator(nn.Module):
    def __init__(self, z_dim, img_chenel, depth_scaling, num_calss, noize_class_embeding):
        super(Generator, self).__init__()
        self.noize_class_embeding = noize_class_embeding
        self.gen = nn.Sequential(nn.ConvTranspose2d(z_dim+noize_class_embeding, depth_scaling*16, 4, 1, 0), #4*4
                               nn.ReLU(),
                               nn.BatchNorm2d(depth_scaling*16),
                               self._block(depth_scaling*16, depth_scaling*8), #8*8
                               self._block(depth_scaling * 8, depth_scaling * 4),#16*16
                               self._block(depth_scaling * 4, depth_scaling * 2),# 32*32
                               nn.ConvTranspose2d(depth_scaling * 2, img_chenel, 4, 2, 1), #64*64
                               nn.Tanh())
        self.embeding = nn.Embedding(num_calss, noize_class_embeding)

    def forward(self, x, lable):
        embed = self.embeding(lable).reshape(lable.shape[0], self.noize_class_embeding).unsqueeze(2).unsqueeze(3)
        x = torch.cat([x, embed], dim=1)
        return self.gen(x)

    def _block(self,in_chanel, out_chanel):
        return nn.Sequential(nn.ConvTranspose2d(in_chanel, out_chanel, 4, 2, 1, bias=False),
                             nn.BatchNorm2d(out_chanel), nn.ReLU())

def initialize_weight(model):
    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.ConvTranspose2d, nn.BatchNorm2d)):
            nn.init.normal(module.weight.data, 0.0, 0.02)
    return model
def gradient_penalty(cretic, real, fake,lable,device):
    cretic=cretic.to(device)
    N, C, H, W = real.shape
    epsilon_ = torch.randn((N, 1, 1, 1)).repeat(1,C,H,W).to(device)
    x = epsilon_*real+(1-epsilon_)*fake
    mixed_output = cretic(x, lable)
    gradient = torch.autograd.grad(outputs=mixed_output, inputs=x, grad_outputs=torch.ones_like(mixed_output),
                                 retain_graph=True, create_graph=True)[0]
    gradient = gradient.reshape(gradient.shape[0], -1)
    gradient_p = gradient.norm(2, dim=1)
    gradient_p_ = torch.mean((gradient_p-1)**2)
    return  gradient_p_


# def test():
#     N, image_chenel,h,w= 5,3,64,64
#     imge_batch=torch.randn((N, image_chenel,h,w))
#     z_dim=100
#     depth_scaling=64
#     noise=torch.randn((N,z_dim,1,1))
#     gen_=Generator(z_dim,image_chenel,depth_scaling)
#     dis_=Critic(image_chenel,depth_scaling)
#     initialize_weight(gen_)
#     initialize_weight(dis_)
#     a=gen_(noise)
#     b=dis_(imge_batch)
#     assert gen_(noise).shape==(N, image_chenel,h,w)
#     assert dis_(imge_batch).shape==(N,1,1,1)
# if __name__=='__main__':
#     test()
#     print('done!')