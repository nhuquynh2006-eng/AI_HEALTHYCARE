import pandas as pd

from sklearn.model_selection import train_test_split

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Đọc dataset
df = pd.read_csv("datasets/diabetes.csv")

# Dữ liệu đầu vào
X = df.drop("Outcome", axis=1)

# Kết quả đầu ra
y = df["Outcome"]

# Chia train/test
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Tạo Deep Learning model
model = Sequential()

model.add(Dense(64, activation='relu', input_shape=(8,)))
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# Compile model
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Train AI
history = model.fit(
    X_train,
    y_train,
    epochs=50,
    batch_size=16
)

# Đánh giá model
loss, accuracy = model.evaluate(X_test, y_test)

print("Accuracy:", accuracy)

# Lưu model AI
model.save("models/diabetes_model.keras")

print("Model saved!")