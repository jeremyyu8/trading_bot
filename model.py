import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import numpy as np
from datetime import datetime

import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

data = pd.read_csv('data.csv')
print("TensorFlow version:", tf.__version__)

train_percent = 0.95
window = 9

# get close values and split into training and
close_data = data.filter(['Close'])
dataset = close_data.values

# scale data between 0 and 1
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset)

# split into train and test
training = int(np.ceil(len(dataset) * train_percent))
print("Numper of training points:", training)
train_data = scaled_data[0:int(training), :]
test_data = scaled_data[int(training):, :]

# split into data points that are of length window and target label that is the next price
x_train = []
y_train = []

for i in range(window, len(train_data)):
    x_train.append(train_data[i-window:i, 0])
    y_train.append(train_data[i, 0])

# convert to numpy array and reshape
x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
print(x_train)

# create LSTM model
model = tf.keras.models.Sequential()
model.add(tf.keras.layers.LSTM(units=64,
                               return_sequences=True,
                               input_shape=(x_train.shape[1], 1)))
model.add(tf.keras.layers.LSTM(units=64))
model.add(tf.keras.layers.Dense(32))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(1))
print(model.summary)

# compile and fit model
model.compile(optimizer='adam',
              loss='mean_squared_error')
history = model.fit(x_train,
                    y_train,
                    epochs=3,
                    batch_size=128)

# preprocess test data same way as train
test_data = scaled_data[training - window:, :]
x_test = []
y_test = dataset[training:, :]
for i in range(window, len(test_data)):
    x_test.append(test_data[i-window:i, 0])

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# predict the testing data
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# evaluation metrics
mse = np.mean(((predictions - y_test) ** 2))
print("MSE", mse)
print("RMSE", np.sqrt(mse))

print(predictions)
print(y_test)

# plot predictions
train = data[training-10000:training]
test = data[training:]
test['Predictions'] = predictions

plt.figure(figsize=(10, 8))
plt.plot(train['Date'], train['Close'])
plt.plot(test['Date'], test[['Close', 'Predictions']])
plt.title('Bitcoin Price')
plt.xlabel('Date')
plt.ylabel("Close")
plt.legend(['Train', 'Test', 'Predictions'])
plt.show()
