import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

print("Loading advanced dataset...")
# Load the newly enriched dataset
df = pd.read_csv('advanced_soil_data.csv')

# 1. Map the text crops to the numeric codes your frontend uses
def encode_crop(crop_name):
    crop = str(crop_name).lower()
    if 'maize' in crop: return 1
    elif 'bean' in crop: return 2
    elif 'wheat' in crop: return 3
    else: return 4 

df['crop_code'] = df['crop_name'].apply(encode_crop)

# 2. Select the Full Spectrum of features (7 chemicals + 1 crop code)
features = [
    'soil_pH', 
    'nitrogen', 
    'phosphorus', 
    'potassium', 
    'organic_carbon', 
    'calcium', 
    'magnesium', 
    'crop_code'
]

X = df[features]
y = df['target_fertilizer']

# 3. Split the data (80% training, 20% testing)
print("Splitting data and training Full-Spectrum Random Forest Model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train the Model (Increased n_estimators for better pattern recognition)
model = RandomForestClassifier(n_estimators=150, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# 5. Test the Accuracy
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"\n--- AI Training Complete ---")
print(f"Old Model Accuracy: 54.59%")
print(f"NEW Model Accuracy on unseen data: {accuracy * 100:.2f}%")

# 6. Export the new, smarter brain!
model_filename = 'soilsync_ai_model.pkl'
joblib.dump(model, model_filename)
print(f"Model successfully saved to {model_filename}")