import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
from torch import optim
import tensorflow as tf
from tensorflow.keras import datasets, layers, models



class ChessValueDataset(Dataset):
  def __init__(self):
    dat = np.load("processed_dataset.npz")
    self.X = dat['arr_0']
    self.Y = dat['arr_1']
    print("loaded", self.X.shape, self.Y.shape)

  def __len__(self):
    return self.X.shape[0]

  def __getitem__(self, idx):
    return (self.X[idx], self.Y[idx])













if __name__ == "__main__":

  # chess_dataset = ChessValueDataset()
  # print(chess_dataset.X[0], chess_dataset.Y[0])
  # print(len(chess_dataset))
  print(tf.__version__)

