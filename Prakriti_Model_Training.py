import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import pickle
from sklearn.metrics import accuracy_score

data = pd.read_csv("Prakriti_Dataset.csv")

print(data.head())

x = data.drop("Dosha", axis=1)
print(x.head())

y = data["Dosha"]
print(y.head())

x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.3)

model = DecisionTreeClassifier()
model.fit(x_train, y_train)

print(model.predict([[54.16,59.09,58.33]]))

y_pred = model.predict(x_test)

accuracy = accuracy_score(y_test, y_pred)
print("Accuracy: ", accuracy)

with open("Prakriti_model.pkl", "wb") as file:
    pickle.dump(model, file)