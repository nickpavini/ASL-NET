import dispatcher
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Activation, MaxPooling2D, Flatten, Dense, Dropout
import matplotlib.pyplot as plt
import sys
from tqdm import tqdm # prettier loops
import numpy as np


# Running Tensorflow 2.1.0

if __name__ == "__main__":

    # Create model
    model = Sequential()
    # Images are 64x64, with 3 channels (RGB)

    # 2D convolutional network with 5x5 filter
    model.add(Conv2D(32, kernel_size=(5, 5),
                        input_shape = (64, 64, 3),
                        activation = 'relu'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2,2)))

    model.add(Conv2D(64, kernel_size=(5, 5),
                        activation = 'relu'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2,2)))

    model.add(Dropout(0.4)) # dropout layer

    model.add(Flatten())
    model.add(Dense(1000, activation='relu'))

    # 26 alphabet letters
    model.add(Dense(26))
    model.add(Activation('softmax'))

    model.compile(loss="sparse_categorical_crossentropy",
                  optimizer='adam',
                  metrics=['accuracy'])

    # handle dataset
    dataset_directory = str(sys.argv[1])
    batch_size = int(sys.argv[2])

    # handle on our dataset
    dataset = dispatcher.Dataset(dataset_directory, batch_size)

    # Train and validate network
    while(dataset.current_epoch < dataset.epoch_threshold): # go for some number of epochs
        # train
        for step in tqdm(range(dataset.train_number_of_batches), desc = "Training Model " + "- Epoch " + str(int(dataset.current_epoch+1))): # for each batch in the epoch
            (train_photos, train_labels) = dataset.generate_train_batch() # get next batch of training images
            train_photos = train_photos / 255.0 # standardize RGB values between 0-1

            stats = model.train_on_batch(train_photos, train_labels)
            #print("Epoch " + str(dataset.current_epoch) + " - Loss & Accuracy: ")
            #print(stats)

        # validate
        num_correct = 0
        total_predictions = 0
        for step in tqdm(range(dataset.val_test_number_of_batches), desc = "Validating Model"): # lets load all in memory then evaluate in test mode for validation
                (val_photos, val_labels) = dataset.generate_val_batch() # get next batch of val images
                predictions = model.predict_on_batch(val_photos)

                # go through and see which predictions are correct
                for i in range(batch_size):
                    if val_labels[i] == np.argmax(predictions[i]):
                        num_correct += 1

                total_predictions += batch_size # we predict batch size at a time

        print("Validation Accuracy: " + str(num_correct/total_predictions))
