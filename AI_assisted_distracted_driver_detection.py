# -*- coding: utf-8 -*-
"""distracted-driver-detection.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1lr9ImuP8np0MKuPe-mfFSsVNyKNl2Azp
"""

!pip install gradio

!pip install gtts

import gradio as gr
import cv2
import numpy as np
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.keras import optimizers
from gtts import gTTS
import tempfile

# Define class labels
class_labels = {
    0: "not distracted - safe driving",
    1: "manual distraction - mobile usage",
    2: "manual distraction - mobile usage",
    3: "manual distraction - mobile usage",
    4: "manual distraction - mobile usage",
    5: "manual distraction - controlling infotainment",
    6: "manual distraction",
    7: "cognitive distraction",
    8: "manual distraction",
    9: "cognitive distraction",
    10: "not distracted - safe driving"
}

# Function to generate voice alert
def generate_alert(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        temp_path = fp.name
        tts.save(temp_path)
    return temp_path

# Load and preprocess the captured or uploaded image
def process_image(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img, (256, 256))
    img_preprocessed = preprocess_input(np.array(img_resized).astype('float32'))
    img_batch = np.expand_dims(img_preprocessed, axis=0)

    # Define and load the model
    conv_base = VGG16(weights='imagenet', include_top=False, input_shape=(256, 256, 3))

    model_DL = Sequential()
    model_DL.add(conv_base)
    model_DL.add(Flatten())
    model_DL.add(Dense(512, activation='relu'))
    model_DL.add(Dropout(0.35))
    model_DL.add(Dense(128, activation='relu'))
    model_DL.add(Dropout(0.35))
    model_DL.add(Dense(32, activation='relu'))
    model_DL.add(Dense(11, activation='softmax'))  # Ensure there are 11 classes

    model_DL.compile(loss='categorical_crossentropy',
                     optimizer=optimizers.Adam(learning_rate=0.0001),
                     metrics=['accuracy'])

    # Make predictions
    predictions = model_DL.predict(img_batch)

    # Decode predictions
    predicted_class = np.argmax(predictions, axis=1)[0]

    # Display the predicted class label
    predicted_label = class_labels[predicted_class]
    print("Predicted class:", predicted_class)
    print("Predicted label:", predicted_label)

    # Set frame color based on predicted class
    if predicted_class == 0 or predicted_class == 10:
        frame_color = (0, 255, 0)  # Green for safe driving
        predicted_label = "Safe driving... go ahead"
    else:
        frame_color = (255, 0, 0)  # Red for distracted driving

    img_with_frame = cv2.rectangle(img_resized, (0, 0), (255, 255), frame_color, 10)

    # Generate and return audio alert file
    audio_filename = generate_alert(predicted_label)

    return img_with_frame, predicted_label, audio_filename

# Define Gradio interface
iface = gr.Interface(
    fn=process_image,
    inputs=gr.components.Image(type="numpy", label="Upload or Capture Image"),
    outputs=[
        gr.components.Image(type="numpy", label="Processed Image"),
        gr.components.Textbox(label="Predicted Label"),
        gr.components.Audio(label="Audio Alert")
    ]
)

# Launch the interface
iface.launch()

