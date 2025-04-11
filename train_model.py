
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load IVF dataset (mocked data)
data = {
    'age': [30, 35, 32, 28],
    'bmi': [22.5, 25.0, 23.8, 21.4],
    'embryo_quality': [3, 4, 2, 5],
    'hormone_level': [200, 180, 210, 190],
    'prev_pregnancies': [0, 1, 0, 2],
    'success': [1, 0, 1, 1]
}

df = pd.DataFrame(data)

features = ['age', 'bmi', 'embryo_quality', 'hormone_level', 'prev_pregnancies']
X = df[features]
y = df['success']

model = RandomForestClassifier()
model.fit(X, y)

pickle.dump(model, open('model.pkl', 'wb'))
print("Model saved as model.pkl")
