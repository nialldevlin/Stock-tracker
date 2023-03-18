from tensorflow import keras
import numpy as np

model = keras.models.load_model('../data/model.h5')

print("Load data")
features = np.loadtxt('../data/f_test.csv', delimiter=",", dtype=float)
features = np.reshape(features, (features.shape[0], features.shape[1], 1))
labels = np.loadtxt('../data/l_test.csv', delimiter=",", dtype=float)

print("Evaluate on test data")
results = model.evaluate(features, labels, batch_size=1024)
print(results)

p_f = features[:3]
print(p_f)
pred = model.predict(p_f)
print(pred)
