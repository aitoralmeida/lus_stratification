import os
import numpy as np
import argparse

from sklearn import metrics
from random import shuffle, sample, seed

import tensorflow as tf
from tensorflow import keras
from tensorflow.random import set_seed
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.applications.mobilenet import MobileNet
from tensorflow.keras.applications.mobilenet import preprocess_input as preprocess_input_v1
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as preprocess_input_v2
from tensorflow.keras.applications.efficientnet import *

#TODO add to args
TEST_SET_PATIENTS = ['04_','09_','18_','21_','27_','36_','38_','41_','51_','55_','59_','60_']

def create_sets(path, positive, negative, model_name, model_version, model, train_test_divide):
  files_covid= os.listdir(path)
  total_files = len(files_covid)
  print ('Total files in disk:', total_files)
  
  #randomize the files
  shuffle(files_covid)

  #find positive and negative files
  print('*'*10)
  print('Separating posititive and negative files...')
  print('Positive token:', positive)
  print('Negative token', negative)
  positive_files = []
  negative_files = []
  for name in files_covid:
    if negative in name:
      negative_files.append(name) 
    elif positive in name:
      positive_files.append(name) 
  total_positive = len(positive_files)
  print ('Total positive files:', total_positive)
  total_negative = len(negative_files)
  print ('Total negative files:', total_negative)
  #sanity check
  print('>>>>>Sanity check...')
  print ('Expected total files:', total_files)
  print ('Total files positive+negative:', total_positive+total_negative)

  #calculating splits
  #train
  total_train_pos = int(total_positive * train_test_divide)
  total_train_neg = int(total_negative * train_test_divide)
  print('*'*10) 
  print('Calculating splits...')
  print('Training positive:', total_train_pos)
  print('Training positive percentage:', float(total_train_pos/(total_train_pos+total_train_neg)))
  print('Training negative:', total_train_neg)
  print('Training negative percentage:', float(total_train_neg/(total_train_pos+total_train_neg)))
  total_train = total_train_pos+total_train_neg
  print('Training total:', total_train)
  #val
  test_pos = total_positive - total_train_pos
  test_neg = total_negative - total_train_neg
  test_total = test_pos + test_neg
  print('Test positive:', test_pos)
  print('Test positive percentage:', float(test_pos/test_total))
  print('Test negative:', test_neg)
  print('Test negative percentage:', float(test_neg/test_total))
  print('Test total:', test_total)
  #sanity check
  print('>>>>>Sanity check...')
  print('Target divide perecentage:', train_test_divide)
  print('Train percentage', (float)(total_train/(total_train+test_total)))
  print('Test percentage', (float)(test_total/(total_train+test_total)))
  print ('Expected total files::', total_files)
  print ('Total files train+val:', total_train+test_total)

  #HASTA AQUI BIEN
  
  print('*'*10)
  print('Loading file names...')
  print('Total positive', len(positive_files))
  print('Total negative', len(negative_files))
  print('Expected train pos:', total_train_pos)
  print('Expected train neg:', total_train_neg)
  #train
  train_positive_filenames = positive_files[:total_train_pos]
  train_negative_filenames = negative_files[:total_train_neg]
  train_files = train_positive_filenames + train_negative_filenames
  #sanity check
  print('>>>>>Sanity check...')
  print('Expected train positive:', total_train_pos)
  print('Actual train positive:', len(train_positive_filenames))
  print('Expected train negative:', total_train_neg)
  print('Actual train negative:', len(train_negative_filenames))
  print('Expected train:', total_train)
  print('Actual files in train_files:', len(train_files))
  #val
  val_positive_filenames = positive_files[total_train_pos:]
  val_negative_filenames = negative_files[total_train_neg:]
  val_files = val_positive_filenames + val_negative_filenames
  #sanity check
  print('>>>>>Sanity check...')
  print('Expected val positive:', test_pos)
  print('Actual val positive:', len(val_positive_filenames))
  print('Expected val negative:', test_neg)
  print('Actual val negative:', len(val_negative_filenames))
  print('Expected val:', test_total)
  print('Actual files in val_files:', len(val_files))
  
  #train_files = positive_files[:total_train_pos] + negative_files[:total_train_neg]
  #val_files = positive_files[total_train_pos:]  + negative_files[total_train_neg:]
    
  shuffle(train_files)
  shuffle(val_files)
  #loading images
  print('Loading train and val images...')
  # Train
  print ('Processing training data...')
  X_train = []
  X_train_names = []
  y_train = []
  fail_train = []
  file_processed = 0
  for filename in train_files:
    file_processed += 1
    if file_processed % 300 == 0:
      print('Processing ', file_processed, 'of', len(train_files))
    if positive in filename: 
      y_train.append([1,0])
    elif negative in filename:
      y_train.append([0,1])
    else: #wrong filename
      fail_train.append(filename)
    img = image.load_img(path+filename, target_size=(224, 224, 3))
    x = image.img_to_array(img)
    if (model_name == "mobilenet"):
        if (model_version == 'V1'):
          x = preprocess_input_v1(x) #mobilenet v1
        elif (model_version == 'V2'):
          x = preprocess_input_v2(x) #mobilenet v2
    X_train.append(x)
    X_train_names.append(filename)
  #sanity check
  print('Sanity check...')
  print('X_train total:', len(X_train))
  print('y_train total:', len(y_train))
  print('fail_train total:', len(fail_train))
  print(fail_train)

  #val
  print ('Processing validation data...')
  X_val = []
  X_val_names = []
  y_val = []
  fail_val = []
  file_processed = 0
  for filename in val_files:
    file_processed += 1
    if file_processed % 300 == 0:
      print('Processing ', file_processed, 'of', len(val_files))
    if positive in filename: 
      y_val.append([1,0])
    elif negative in filename:
      y_val.append([0,1])
    else: #wrong filename
      fail_val.append(filename)
    img = image.load_img(path+filename, target_size=(224, 224, 3))
    x = image.img_to_array(img)
    if (model_name == "mobilenet"):
        if (model_version == 'V1'):
          x = preprocess_input_v1(x) #mobilenet v1
        elif (model_version == 'V2'):
          x = preprocess_input_v2(x) #mobilenet v2
    X_val.append(x)
    X_val_names.append(filename)

  #sanity check
  print('Sanity check...')
  print('X_val total:', len(X_val))
  print('y_val total:', len(y_val))
  print('fail_val total:', len(fail_val))
  print(fail_val)

  X_train = np.array(X_train)
  y_train = np.array(y_train)
  X_val = np.array(X_val)
  y_val = np.array(y_val)  
  print('Shapes train')
  print(X_train.shape)
  print(y_train.shape)
  print('Shapes val')
  print(X_val.shape)
  print(y_val.shape)
  return X_train, y_train, X_train_names, X_val, y_val, X_val_names

def create_sets_by_patients(path, positive, negative, model_name, model_version, model, train_test_divide):
  files_covid= os.listdir(path)
  total_files = len(files_covid)
  print ('Total files in disk:', total_files)

  train_files = []
  val_files = []

  for filename in files_covid:
    if any(x in filename for x in TEST_SET_PATIENTS):
      val_files.append(filename)
    else:
      train_files.append(filename)

  print('Total train files:', len(train_files))
  print('Total test files:', len(val_files))
 
  #loading images
  print('Loading train and val images...')
  # Train
  print ('Processing training data...')
  X_train = []
  X_train_names = []
  y_train = []
  fail_train = []
  file_processed = 0
  for filename in train_files:
    file_processed += 1
    if file_processed % 300 == 0:
      print('Processing ', file_processed, 'of', len(train_files))
    if positive in filename: 
      y_train.append([1,0])
    elif negative in filename:
      y_train.append([0,1])
    else: #wrong filename
      fail_train.append(filename)
    img = image.load_img(path+filename, target_size=(224, 224, 3))
    x = image.img_to_array(img)
    if (model_name == "mobilenet"):
        if (model_version == 'V1'):
          x = preprocess_input_v1(x) #mobilenet v1
        elif (model_version == 'V2'):
          x = preprocess_input_v2(x) #mobilenet v2
    X_train.append(x)
    X_train_names.append(filename)
  #sanity check
  print('Sanity check...')
  print('X_train total:', len(X_train))
  print('y_train total:', len(y_train))
  print('fail_train total:', len(fail_train))
  print(fail_train)
  
  #val
  print ('Processing validation data...')
  X_val = []
  X_val_names = []
  y_val = []
  fail_val = []
  file_processed = 0
  test_pos_total = 0
  test_neg_total = 0
  for filename in val_files:
    file_processed += 1
    if file_processed % 300 == 0:
      print('Processing ', file_processed, 'of', len(val_files))
    if positive in filename: 
      y_val.append([1,0])
      test_pos_total += 1
    elif negative in filename:
      y_val.append([0,1])
      test_neg_total += 1
    else: #wrong filename
      fail_val.append(filename)
    img = image.load_img(path+filename, target_size=(224, 224, 3))
    x = image.img_to_array(img)
    if (model_name == "mobilenet"):
        if (model_version == 'V1'):
          x = preprocess_input_v1(x) #mobilenet v1
        elif (model_version == 'V2'):
          x = preprocess_input_v2(x) #mobilenet v2
    X_val.append(x)
    X_val_names.append(filename)

  #sanity check
  print('Sanity check...')
  print('X_val total:', len(X_val))
  print('y_val total:', len(y_val))
  print('fail_val total:', len(fail_val))
  print(fail_val)
  print('Test positive examples:', test_pos_total)
  print((float)(test_pos_total/len(y_val)))
  print('Test negative examples:', test_neg_total)
  print((float)(test_neg_total/len(y_val)))

  X_train = np.array(X_train)
  y_train = np.array(y_train)
  X_val = np.array(X_val)
  y_val = np.array(y_val)  
  print('Shapes train')
  print(X_train.shape)
  print(y_train.shape)
  print('Shapes val')
  print(X_val.shape)
  print(y_val.shape)
  return X_train, y_train, X_train_names, X_val, y_val, X_val_names

if __name__ == '__main__':
    # parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",
                        type=str,
                        default='mobilenet',
                        nargs="?",
                        help="Model: mobilenet or efficientnet.")
    parser.add_argument("--model_version",
                        type=str,
                        default='V1',
                        nargs="?",
                        help="Mobile net version: V1 or V2. Efficient net scaling: B0, B1, B2, B3, B4, B5, B6 or B7.")
    parser.add_argument("--dataset_path",
                        type=str,
                        default='/lus_stratification/generate_model/croppedi2p0/',
                        nargs="?",
                        help="Dataset's absolute path")
    parser.add_argument("--results_path",
                        type=str,
                        default='/lus_stratification/generate_model/results/',
                        nargs="?",
                        help="Results's absolute path")
    parser.add_argument("--train_test_divide",
                        type=float,
                        default=0.75,
                        nargs="?",
                        help="Train test divide value between 0.0 and 1.0")
    parser.add_argument("--epochs",
                        type=int,
                        default=10,
                        nargs="?",
                        help="Epochs value between 1 and infinite")
    parser.add_argument("--batch_size",
                        type=int,
                        default=32,
                        nargs="?",
                        help="Batch size value")
    parser.add_argument("--steps_per_epoch",
                        type=int,
                        default=300,
                        nargs="?",
                        help="Steps per epoch value")
    parser.add_argument("--use_steps_per_epoch",
                        type=int,
                        default=0,
                        nargs="?",
                        help="Use steps per epoch value: 1 use, other not use. Default 0.")
    parser.add_argument("--optimizer",
                        type=str,
                        default='adam',
                        nargs="?",
                        help="Optimizer")
    parser.add_argument("--loss",
                        type=str,
                        default='binary_crossentropy',
                        nargs="?",
                        help="Loss")
    parser.add_argument("--label_dataset_zero",
                        type=str,
                        default='N0',
                        nargs="?",
                        help="Label dataset 0: N0, B0, M0, S0, C0, P0.")
    parser.add_argument("--label_dataset_one",
                        type=str,
                        default='N1',
                        nargs="?",
                        help="Label dataset 1: N1, B1, M1, S1, C1, P1.")
    parser.add_argument("--strategy",
                        type=str,
                        default='combined',
                        nargs="?",
                        help="Create sets strategy: combined or by_patients.")
    parser.add_argument("--random_seed",
                        type=int,
                        default=12345,
                        nargs="?",
                        help="Random seed for reproducible results")
    args = parser.parse_args()

    # reproducible results
    os.environ['PYTHONHASHSEED'] = '0'
    np.random.seed(args.random_seed)
    seed(args.random_seed)
    set_seed(args.random_seed)

    # get the model without the denses
    if (args.model == 'mobilenet'):
      if (args.model_version == 'V1'):
        base_model = MobileNet(weights='imagenet', include_top=False)
      elif (args.model_version == 'V2'):
        base_model = MobileNetV2(weights='imagenet', include_top=False)
    elif (args.model == 'efficientnet'):
      if args.model_version == 'B0':
        base_model = EfficientNetB0(weights='imagenet', include_top=False)
      if args.model_version == 'B1':
        base_model = EfficientNetB1(weights='imagenet', include_top=False)
      if args.model_version == 'B2':
        base_model = EfficientNetB2(weights='imagenet', include_top=False)
      if args.model_version == 'B3':
        base_model = EfficientNetB3(weights='imagenet', include_top=False)
      if args.model_version == 'B4':
        base_model = EfficientNetB4(weights='imagenet', include_top=False)
      if args.model_version == 'B5':
        base_model = EfficientNetB5(weights='imagenet', include_top=False)
      if args.model_version == 'B6':
        base_model = EfficientNetB6(weights='imagenet', include_top=False)
      if args.model_version == 'B7':
        base_model = EfficientNetB7(weights='imagenet', include_top=False)

    last_layer = base_model.layers[-1]
    
    new_top_layer_global_avg_pooling = GlobalAveragePooling2D()(last_layer.output)
    new_dense = Dense(1024, activation='relu')(new_top_layer_global_avg_pooling)
    predictions = Dense(2, activation='softmax')(new_dense)
    model = Model(base_model.input, predictions)

    # we will only train the new denses for the baseline
    for layer in base_model.layers:
      layer.trainable = False

    # compile model
    model.compile(optimizer=args.optimizer, loss=args.loss, metrics = ["accuracy"])

    # see model structure
    model.summary()

    # get the data
    print('***** Load files...')
    if args.strategy == 'combined':
      X_train, y_train, X_train_names, X_val, y_val, X_val_names = create_sets(args.dataset_path,
        args.label_dataset_zero,
        args.label_dataset_one,
        args.model,
        args.model_version,
        model,
        args.train_test_divide)
    elif args.strategy == 'by_patients':
      X_train, y_train, X_train_names, X_val, y_val, X_val_names = create_sets_by_patients(args.dataset_path,
        args.label_dataset_zero,
        args.label_dataset_one,
        args.model,
        args.model_version,
        model,
        args.train_test_divide)
    
    # fit model
    if (args.use_steps_per_epoch == 1):
      results = model.fit(X_train, y_train, epochs=args.epochs, steps_per_epoch=args.steps_per_epoch, batch_size=args.batch_size, validation_data=(X_val, y_val))
    else:
      results = model.fit(X_train, y_train, epochs=args.epochs, batch_size=args.batch_size, validation_data=(X_val, y_val))

    print('#' * 40)
    print("Finished! Saving model")

    # save model
    model.save(args.results_path + 'covid19_model_' 
      + args.model + args.model_version + "_for_" + args.label_dataset_zero + "_" + args.label_dataset_one)

    print('#' * 40)
    print("Model saved!")
