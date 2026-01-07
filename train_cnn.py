import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt 


DATASET_DIR = 'dataset'
MODEL_DIR = 'models'
IMG_SIZE = (128, 128) 
BATCH_SIZE = 32
EPOCHS = 8 


if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)


train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

validation_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_DIR, 'train'),
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary', 
    shuffle=True
)

validation_generator = validation_datagen.flow_from_directory(
    os.path.join(DATASET_DIR, 'validation'),
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary'
)


model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(512, activation='relu'),
    Dropout(0.5), 
    Dense(1, activation='sigmoid') 
])

model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

model.summary()

print("Eğitim başlıyor... Bu işlem bilgisayar hızına göre 5-15 dk sürebilir.")
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=validation_generator,
    verbose=1
)


model_path = os.path.join(MODEL_DIR, 'hand_gesture_model.h5')
model.save(model_path)
print(f"Model başarıyla eğitildi ve kaydedildi: {model_path}")


print("Eğitim grafikleri oluşturuluyor...")
plt.figure(figsize=(12, 5))


plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Eğitim Başarısı', color='blue', linewidth=2)
plt.plot(history.history['val_accuracy'], label='Doğrulama Başarısı', color='orange', linewidth=2)
plt.title('Model Doğruluğu (Accuracy)')
plt.xlabel('Epoch')
plt.ylabel('Doğruluk')
plt.legend()
plt.grid(True)


plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Eğitim Kaybı', color='red', linewidth=2)
plt.plot(history.history['val_loss'], label='Doğrulama Kaybı', color='darkred', linewidth=2)
plt.title('Model Kaybı (Loss)')
plt.xlabel('Epoch')
plt.ylabel('Kayıp')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('egitim_raporu.png')
print("Grafik 'egitim_raporu.png' olarak kaydedildi!")
# ----------------------------------------

print("Sınıf İndeksleri:", train_generator.class_indices)