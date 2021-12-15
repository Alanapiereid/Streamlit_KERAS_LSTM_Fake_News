import tensorflow as tf
from tensorflow.keras.datasets import imdb
from tensorflow.keras.layers import Embedding, Dense, LSTM
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import model_from_json
import pandas as pd
from sklearn.model_selection import train_test_split


# obtain the original files (login/api credentials needed) from https://www.kaggle.com/c/fake-news/data
df_1 = pd.read_csv('train.csv')
df_1 = df_1.dropna()

#df = df[df['EPS'].notna()]
#df_1.to_csv("cleaned_f-news.csv", index=False)
    

tokenizer = Tokenizer(num_words=50000, oov_token='<UNK>')
# Model configuration
additional_metrics = ['accuracy']
batch_size = 128
embedding_out_dim = 100
loss_function = BinaryCrossentropy()
maxlen = 300
num_d_words = 50000
number_of_epochs = 2
optimizer = Adam()
validation_split = 0.20
verbosity_mode = 1

texts = df_1['text']
labels = df_1['label']

tokenizer = Tokenizer(num_words=num_d_words, filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', lower=True)
# crucial
tokenizer.fit_on_texts(texts.values)
word_index = tokenizer.word_index

#crucial
X = tokenizer.texts_to_sequences(texts.values)
X = pad_sequences(X, maxlen=maxlen)
y = labels.values

x_train, x_test, y_train, y_test = train_test_split(
    X, y, stratify=labels,
    random_state=0)

print(x_train.shape)
print(x_test.shape)


# Define the Keras model
model = Sequential()
model.add(Embedding(num_d_words, embedding_out_dim, input_length=maxlen))
model.add(LSTM(10))
model.add(Dense(1, activation='sigmoid'))

# # Compile the model
model.compile(optimizer=optimizer, loss=loss_function, metrics=additional_metrics)

# # Give a summary
model.summary()

# # Train the model
history = model.fit(x_train, y_train, batch_size=batch_size, epochs=number_of_epochs, verbose=verbosity_mode, validation_split=validation_split)

# # Test the model after training
results = model.evaluate(x_test, y_test, verbose=False)
print(f'Results - Loss: {results[0]} - Accuracy: {100*results[1]}%')

model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# save weights
model.save_weights("model.h5")
print("Saving.....")

json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights
loaded_model.load_weights("model.h5")
print("Loaded")

loaded_model.compile(loss=loss_function, optimizer=optimizer, metrics=additional_metrics)
score = loaded_model.evaluate(X, y, verbose=0)
print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))
