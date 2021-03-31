# -*- coding: utf-8 -*-
"""Task1_Word_Embeddings.ipynb

Automatically generated by Colaboratory.


# Task 1: Word Embeddings (10 points)

This notebook will guide you through all steps necessary to train a word2vec model (Detailed description in the PDF).

## Imports

The following are the packages used
"""

# Imports
import torch
torch.manual_seed(10)
from torch.autograd import Variable
import pandas as pd
import numpy as np
import sklearn as sk
import re
import itertools
import warnings
warnings.filterwarnings("ignore")
import nltk
import torch.nn as  nn
import torch.optim as optim
import torch.nn.functional as F

"""# 1.1 Get the data (0.5 points)

Load it into a data structure of your choice. Then, split off a small part of the corpus as a development set (~100 data points).


The file hindi_hatespeech.tsv is uploaded into a variable "data". The data from columns - "text" and "task_1" is extracted and saved into X_TRAIN and Y_LABEL respectively. 
"""

#TODO: implement!
from google.colab import files
uploaded = files.upload()
#load data
data = pd.read_csv("hindi_hatespeech.tsv",sep='\t')

#split off a small part of the corpus as a development set (~100 data points)
from sklearn.model_selection import train_test_split
train_dev,test_dev = train_test_split(data,train_size=0.025,random_state=123) #random split off the dataset

y_label_dev = train_dev['task_1'].values #extract labels of development set
x_train_dev = train_dev['text'].values  #extract sentences of development set
print(len(y_label_dev))

from sklearn.model_selection import train_test_split
train_dev1,test_dev = train_test_split(data,train_size=0.5,random_state=123) 
#more data trained

X_TRAIN = train_dev1['text'].values # full dataset for sentence trained
Y_LABEL = train_dev1['task_1'].values # full dataset for labels trained

#extract label of dataset
def data_to_label(label):
  y_number = []
  for i in range(len(label)):
    if label[i]=='HOF':
      y_number.append(1)
    elif label[i]=='NOT':
      y_number.append(0)
  return y_number
#assign numbers of labels of development set

y_train = data_to_label(Y_LABEL)

"""## 1.2 Data preparation (0.5 + 0.5 points)

* Prepare the data by removing everything that does not contain information. 
User names (starting with '@') and punctuation symbols clearly do not convey information, but we also want to get rid of so-called [stopwords](https://en.wikipedia.org/wiki/Stop_word), i. e. words that have little to no semantic content (and, but, yes, the...). Hindi stopwords can be found [here](https://github.com/stopwords-iso/stopwords-hi/blob/master/stopwords-hi.txt) Then, standardize the spelling by lowercasing all words.
Do this for the development section of the corpus for now.

* What about hashtags (starting with '#') and emojis? Should they be removed too? Justify your answer in the report, and explain how you accounted for this in your implementation.
"""

#TODO: implement!
#clean the development data set
uploaded = files.upload()
stopwords = pd.read_csv('stopwords-hi.txt',header=None)
stop_words=stopwords[0].tolist()
punc=r'''!()-[]{};:'"\,<>./?@#$%^&*_“~'''

new_list=[]

for i in range(0,len(x_train_dev)):
  # Punctuations removal
  new=' '.join(word for word in x_train_dev[i].split() if word[0] not in punc)
  new = ' '.join(re.sub("(\w+:\/\/\S+)", " ", new).split())
  new = ' '.join(re.sub(r"\b\d+\b", " ", new).split())
  new = ' '.join(re.sub("[\.\,\!\?\:\;\-\=\#\%\…\\u200d\।।]", " ", new).split())
  new = ' '.join(re.sub("[\U0001F600-\U0001F64F]"," ",new).split()) # emotions
  new = ' '.join(re.sub("[\U0001F300-\U0001F5FF]"," ",new).split()) # symbols & pictographs                           
  new = ' '.join(re.sub("[\U0001F680-\U0001F6FF]"," ",new).split()) # transport & map symbols                         
  new = ' '.join(re.sub("[\U0001F1E0-\U0001F1FF]"," ",new).split()) # flags (iOS)  
  new = ' '.join(re.sub("[\U00002702-\U000027B0]"," ",new).split())  
  new = ' '.join(re.sub("[\U000024C2-\U0001F251]"," ",new).split()) 
  new = ' '.join(re.sub("[\U00001F92C]"," ",new).split()) 
  # Converting into lowercase
  new= new.lower()
  # Removing stop words
  new=' '.join(word for word in new.split() if word not in stop_words)
  # Appending to the text list
  new_list.append(new)

#final_data_dev=pd.Series(new_list,dtype="string")
print(len(new_list))

uploaded = files.upload()
stopwords = pd.read_csv('stopwords-hi.txt',header=None)

#clean the full data set
def clean_the_data(data):
  new_list=[]
  punc=r'''!()-[]{};:'"\,<>./?@#$%^&*_“~'''
  stop_words=stopwords[0].tolist()
  for i in range(0,len(data)):
    # Punctuations removal
    new=' '.join(word for word in data[i].split() if word[0] not in punc)
    new = ' '.join(re.sub("(\w+:\/\/\S+)", " ", new).split())
    new = ' '.join(re.sub(r"\b\d+\b", " ", new).split())
    new = ' '.join(re.sub("[\.\,\!\?\:\;\-\=\#\%\…\\u200d\।।]", " ", new).split())
    # Converting into lowercase
    new= new.lower()
    # Removing stop words
    new=' '.join(word for word in new.split() if word not in stop_words)
    # Appending to the text list
    new_list.append(new)
  return new_list

new_list=clean_the_data(X_TRAIN)
print(new_list[0])

nltk.download('punkt')

# Tokenizes each sentence by implementing the nltk tool
new_list_new = [nltk.tokenize.word_tokenize(x) for x in new_list]

"""## 1.3 Build the vocabulary (0.5 + 0.5 points)

The input to the first layer of word2vec is an one-hot encoding of the current word. The output of the model is then compared to a numeric class label of the words within the size of the skip-gram window. Now

* Compile a list of all words in the development section of your corpus and save it in a variable ```V```.
"""

#TODO: implement!

V = {}
i=0
for s in range(len(new_list_new)):
  n=new_list_new[s]
  for y in range(len(n)):
    w=new_list_new[s][y]
    if w not in V:
      V[w] = i
      i+=1
    y+=1
  s+=1
    
print(len(V))

"""* Then, write a function ```word_to_one_hot``` that returns a one-hot encoding of an arbitrary word in the vocabulary. The size of the one-hot encoding should be ```len(v)```."""

#TODO: implement!
# translate words to integer numbers

def word_to_one_hot(word):
  words = V.keys()
  str_to_int = dict((c, i) for i, c in enumerate(words))
  integer_encoded = [str_to_int[string] for string in [word]]
# one hot encode
  onehot_encoded = []
  for value in integer_encoded:
	     letter = [0 for _ in range(len(V))]
	     letter[value] = 1
	     onehot_encoded.append(letter)
  #onehot_encoded.long()
  return onehot_encoded
  pass


#a=word_to_one_hot(new_list_new[1][5])
#print(a)

"""## 1.4 Subsampling (0.5 points)

The probability to keep a word in a context is given by:

$P_{keep}(w_i) = \Big(\sqrt{\frac{z(w_i)}{0.001}}+1\Big) \cdot \frac{0.001}{z(w_i)}$

Where $z(w_i)$ is the relative frequency of the word $w_i$ in the corpus. Now,
* Calculate word frequencies
* Define a function ```sampling_prob``` that takes a word (string) as input and returns the probabiliy to **keep** the word in a context.
"""

#TODO: implement!
Words = {}
i=0
for s in range(len(new_list_new)):
  n=new_list_new[s]
  for y in range(len(n)):
    w=new_list_new[s][y]
    Words[w] = i
    i+=1
    y+=1
  s+=1
W2=list(Words)
def sampling_prob(word):
    frac = W2.count(word)/len(W2)
    prob = (np.sqrt(frac/0.000001) + 1) * (0.000001/frac)
    return prob
    pass

"""# 1.5 Skip-Grams (1 point)

Now that you have the vocabulary and one-hot encodings at hand, you can start to do the actual work. The skip gram model requires training data of the shape ```(current_word, context)```, with ```context``` being the words before and/or after ```current_word``` within ```window_size```. 

* Have closer look on the original paper. If you feel to understand how skip-gram works, implement a function ```get_target_context``` that takes a sentence as input and [yield](https://docs.python.org/3.9/reference/simple_stmts.html#the-yield-statement)s a ```(current_word, context)```.

* Use your ```sampling_prob``` function to drop words from contexts as you sample them. 
"""

#TODO: implement!
def get_target_context(sentence):
    word_lists=[]
    for i in range(len(sentence)):
       w=sentence[i]
       p_sample = sampling_prob(w)
       threshold = np.random.random()
       #print(threshold)
       if p_sample > threshold:
         # the word is kept
         for n in range(2):
                # look back
            if (i-n-1)>=0:
              word_lists.append([w] + [sentence[i-n-1]])
                
                # look forward
            if (i+n+1)<len(sentence):
              word_lists.append([w]+[sentence[i+n+1]])
       else:
         # the word is dropped
         i+=1
    return word_lists
    pass

"""# 1.6 Hyperparameters (0.5 points)

According to the word2vec paper, what would be a good choice for the following hyperparameters? 

* Embedding dimension
* Window size

Initialize them in a dictionary or as independent variables in the code block below. 
"""

# Set hyperparameters
window_size = 2
embedding_size = 64

# More hyperparameters
learning_rate = 0.05
epochs = 10

"""# 1.7 Pytorch Module (0.5 + 0.5 + 0.5 points)

Pytorch provides a wrapper for your fancy and super-complex models: [torch.nn.Module](https://pytorch.org/docs/stable/generated/torch.nn.Module.html). The code block below contains a skeleton for such a wrapper. Now,

* Initialize the two weight matrices of word2vec as fields of the class.

* Override the ```forward``` method of this class. It should take a one-hot encoding as input, perform the matrix multiplications, and finally apply a log softmax on the output layer.

* Initialize the model and save its weights in a variable. The Pytorch documentation will tell you how to do that.
"""

vocabulary_size=len(V)
class Word2Vec(nn.Module):

    def __init__(self, embed_size, vocab_size):
        super(Word2Vec, self).__init__()
        self.input = nn.Embedding(vocab_size, embedding_size)
        self.output = nn.Linear(embedding_size, vocab_size,bias=False)


    def forward(self, one_hot):
        #one_hot = torch.tensor(one_hot）
        
        emb = self.input(one_hot)
        hidden = self.output(emb)
        out = F.log_softmax(hidden)
        return out
# Initialize model
net = Word2Vec(embed_size=embedding_size, vocab_size=vocabulary_size)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
net = net.to(device)

#W1 = net.input.weight
#W2 = net.output.weight
#print(torch.cuda.is_available())
#M = word_to_one_hot('रन')

"""# 1.8 Loss function and optimizer (0.5 points)

Initialize variables with [optimizer](https://pytorch.org/docs/stable/optim.html#module-torch.optim) and loss function. You can take what is used in the word2vec paper, but you can use alternative optimizers/loss functions if you explain your choice in the report.
"""

# Define optimizer and loss
optimizer = torch.optim.SGD(net.parameters(), lr=learning_rate)
criterion = nn.CrossEntropyLoss()

"""# 1.9 Training the model (3 points)

As everything is prepared, implement a training loop that performs several passes of the data set through the model. You are free to do this as you please, but your code should:

* Load the weights saved in 1.6 at the start of every execution of the code block
* Print the accumulated loss at least after every epoch (the accumulate loss should be reset after every epoch)
* Define a criterion for the training procedure to terminate if a certain loss value is reached. You can find the threshold by observing the loss for the development set.

You can play around with the number of epochs and the learning rate.
"""

# load initial weights
window_size = 2
embedding_size = 64
i=0
losses = [torch.tensor(1., device=device)]
#losses.append(1)
losses_mean=np.mean([tensor.cpu() for tensor in losses])
def train():
  
  print("Training started")

train()

for epo in range(epochs):
  while losses_mean> 0.001:
     losses_mean=np.mean([tensor.cpu() for tensor in losses])
     #mean = torch.mean(torch.stack(losses))
     #mean = mean.to(device)
     print("Loss: ", losses_mean)
     net.train() 
    
     for i in range(len(new_list_new)):
        # Define train procedure
        # step1:Skip-Grams
        sentence = new_list_new[i]
        idx_pairs = get_target_context(sentence)
        for target, context in idx_pairs:
        # step2:target one-hot encoding
           X = word_to_one_hot(target)
           X = torch.tensor(X)
           x1 = X[0]
           x1 = x1.to(device)
           #print(x1)
        # step3:Word2Vec
           y =net.forward(x1)
        
           Y = word_to_one_hot(context)
           Y = Y[0]
           y_ture = torch.tensor(Y)
           y_ture = y_ture.to(device)
        # step4:loss
           loss = criterion(y,y_ture)
           #print(loss)
           losses.append(loss.data)
           losses.pop(0)
           optimizer.zero_grad()
           loss.backward()
           optimizer.step()
          
        # step5:Backprop to update model parameters 
   
           
print("Training finished")  


"""# 1.10 Train on the full dataset (0.5 points)

Now, go back to 1.1 and remove the restriction on the number of sentences in your corpus. Then, reexecute code blocks 1.2, 1.3 and 1.6 (or those relevant if you created additional ones). 

* Then, retrain your model on the complete dataset.

* Now, the input weights of the model contain the desired word embeddings! Save them together with the corresponding vocabulary items (Pytorch provides a nice [functionality](https://pytorch.org/tutorials/beginner/saving_loading_models.html) for this).
"""

#torch.save(net.state_dict(), '/content/drive/MyDrive/Colab Notebooks')
torch.save(net.state_dict(),'netweight1.pt')
net.load_state_dict(torch.load('netweight1.pt'))
net.eval()
W1=net.input.weight
print(net.input.weight)

"""Task 2.1 Binary neural sentiment classifier"""

Weight3=[]
for i in range(len(V)-1):
  weight3=[]
  w=W1[i]
  for y in range(embedding_size):
    wei=w[y].item()
    weight3.append(wei)
  Weight3.append(weight3)
    

V2 = dict(zip(V, Weight3))
print(len(V2))

sentence_padding =[]
pad_idx = 0
padding_standard = max(new_list_new, key=len,default='')

#padding the sentence to the same length
for i in range(len(new_list_new)):
  temp_sentence = list()
  temp = new_list_new[i]
  while len(temp) < len(padding_standard):
      temp.insert(len(temp), pad_idx)
  sentence_padding.append(temp) 

#make sentences to the same size matrix using word embedding expression
sentence_train=[]
for i in range(len(sentence_padding)):
  temp_sentence = list()
  temp = new_list_new[i]
  for word in temp:
    if word in V2.keys():
      temp_sentence.append(V2[word])
    else:
      temp_sentence.append(np.zeros(embedding_size))
  sentence_train.append(temp_sentence)

print(np.shape(sentence_train))

sentence_train3=torch.tensor(sentence_train)

from google.colab import drive
drive.mount('/content/drive')
import sys
sys.path.append('/content/drive/MyDrive/Colab Notebooks')

#TASK 2 CLASSIFIER:using CNN for HINDI
from modelinput import CNN

EMBEDDING_DIM = embedding_size 
N_FILTERS = 100
FILTER_SIZES = [2,3,4]
OUTPUT_DIM = 1
DROPOUT = 0.5

model = CNN(EMBEDDING_DIM, N_FILTERS, FILTER_SIZES, OUTPUT_DIM, DROPOUT)

optimizer1 = optim.Adam(model.parameters())

criterion1 = nn.BCEWithLogitsLoss()

model = model.to(device)
criterion1 = criterion1.to(device)

from modelinput import binary_accuracy

N_EPOCHS = 50
sentence_train3=sentence_train3.to(device,dtype=torch.float)
Y_train = torch.tensor(y_train).to(device)

for epoch in range(N_EPOCHS):
    epoch_loss = 0
    epoch_acc = 0
    
    model.train()
  
    optimizer1.zero_grad()

    predictions = model.forward(sentence_train3).squeeze(1)    
    loss1 = criterion1(predictions, Y_train.float())
    #print(np.shape(predictions))   
    acc = binary_accuracy(predictions, Y_train)

    loss1.backward()    
    optimizer1.step()
        
    epoch_loss += loss1.item()
    epoch_acc += acc.item()
    
    
    
    
    
    
    print(f'\tTrain Loss: {loss1:.3f} | Train Acc: {acc*100:.2f}%')

def evaluate(model):
    
    epoch_loss = 0
    epoch_acc = 0
    
    model.eval()
    
    predictions = model(sentence_train3).squeeze(1)
            
    loss = criterion1(predictions, Y_train.float())
            
    acc = binary_accuracy(predictions, Y_train)

    epoch_loss += loss.item()
    epoch_acc += acc.item()
        
    return epoch_loss, epoch_acc 
test_loss, test_acc = evaluate(model)
print(f'Test Loss: {test_loss:.3f} | Test Acc: {test_acc*100:.2f}%')

torch.save(model.state_dict(),'CNNmodelweight.pt')

#Task3:Transformer Implement,trying to improve the accuracy of CNN

import copy

def clones(module, N):
    "Produce N identical layers."
    return nn.ModuleList([copy.deepcopy(module) for _ in range(N)])

import math
#doing the position encoding first
def positionalencoding1d(d_model, length):
   
    if d_model % 2 != 0:
        raise ValueError("Cannot use sin/cos positional encoding with "
                         "odd dim (got dim={:d})".format(d_model))
    pe = torch.zeros(length, d_model)
    position = torch.arange(0, length).unsqueeze(1)
    div_term = torch.exp((torch.arange(0, d_model, 2, dtype=torch.float) *
                         -(math.log(10000.0) / d_model)))
    pe[:, 0::2] = torch.sin(position.float() * div_term)
    pe[:, 1::2] = torch.cos(position.float() * div_term)

    return pe


posit = positionalencoding1d(64,61) # the shape of one padding sentence
posit = torch.tensor(posit,device=device)

AttInput=torch.empty(np.shape(sentence_train3))

for i in range(len(sentence_train3)):
   tar =sentence_train3[i]
   AttInput[i]= tar+posit

SRC_VOCAB=1
N_CLASS=1
D_MODEL=embedding_size
D_FF=1024
N = 6
H=8
DROP_OUT=0.1

import modelinput
model2 = modelinput.make_model(SRC_VOCAB,N,D_MODEL,D_FF,H,DROP_OUT, N_CLASS)
model2 = model2.to(device)

lr=0.005
criterion2 = nn.CrossEntropyLoss()
optimizer2 = torch.optim.Adam(model2.parameters(),lr)
N_EPOCHS = 10

torch.cuda.empty_cache()

for epoch in range(N_EPOCHS):
    epoch_loss2 = 0
    epoch_acc2 = 0   
  
    optimizer2.zero_grad()

    x = AttInput.to(device)
    y = torch.tensor(y_train, dtype=torch.long, device=device)
    y = y.unsqueeze(1)
    
    output = model2(x, None)
    loss2 = criterion2(output,y)
     

    loss2.backward()    
    optimizer2.step()
        
    epoch_loss2 += loss2.item()
   
    print(f'\tTrain Loss: {loss2:.3f}')
