# Conditional_GAN
The goal is to implement the Conditional GAN from Scratch.

1- Here we use Wasserstein GAN with Gradient pnalty as our baseline for implementation. Moreover, the Generator and Discriminator architectures are 
CNN. Models and architecture are defined in C_GAN_model.py and training is done in C_GAN_train.py.

2- Increase feature_dim in C_GAN_train.py to 16, 32, 64 for better results if you have more computation power. Other hyperparameters (number of epoch, Z_dimension) are defined in the same file, increasing them potentially increase the performance as well.  

