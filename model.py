"""Demo ML predictor. Trains a Logistic Regression model on generated sample data.
Replace generated data with a real, ethically collected placement dataset for research use."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

_rng = np.random.default_rng(42)
X = np.column_stack([
    _rng.uniform(4.0, 10.0, 800),   # CGPA
    _rng.uniform(20, 100, 800),     # Aptitude score
    _rng.uniform(20, 100, 800),     # Communication score
    _rng.integers(0, 5, 800),       # Internships
    _rng.integers(0, 6, 800),       # Projects
])
score = (X[:,0]*8 + X[:,1]*0.20 + X[:,2]*0.18 + X[:,3]*3 + X[:,4]*2.5)
y = (score > 105).astype(int)
_model = make_pipeline(StandardScaler(), LogisticRegression(random_state=42))
_model.fit(X, y)

def predict_placement(cgpa, aptitude, communication, internships, projects):
    sample = np.array([[cgpa, aptitude, communication, internships, projects]])
    probability = float(_model.predict_proba(sample)[0][1] * 100)
    label = "Placed" if probability >= 50 else "Not Placed"
    return label, round(probability, 2)
