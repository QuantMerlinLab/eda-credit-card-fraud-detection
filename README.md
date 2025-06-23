# :detective: EDA & Credit Card Fraud Detection
![Credit Cards Used in the US](https://github.com/QuantMerlinLab/eda-credit-card-fraud-detection/raw/main/images/us_credit_cards.jpg)
![Fraud Rate by U.S. State](https://github.com/QuantMerlinLab/eda-credit-card-fraud-detection/raw/main/images/fraud_map_usa.png)

## 📜 License
This project is open-source under the [MIT License](https://opensource.org/license/MIT).   
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)   
*Copyright © 2025 - [QuantMerlinLab](https://github.com/QuantMerlinLab)* 

## :pushpin: Project Info
## 👨‍💻 Author Info 
**Merlin KENGMO YONTA**  
### 📬 Contact
Feel free to reach out to me via:
- ✉️ Email: [kengmoyontamerlin@gmail.com](mailto:kengmoyontamerlin@gmail.com)  
- 💬 WhatsApp: [Click here to message me](https://wa.me/237672718383?text=Hello%2C%20I%20found%20you%20through%20your%20GitHub%20README)  
- 🌐 LinkedIn: [linkedin.com/in/merlin-kengmo-yonta](https://www.linkedin.com/in/merlin-kengmo-yonta-90bb64303/)  
> _Please mention the subject of your message so I can respond accordingly._

-  ## Analyzed Data
-  ### Interactive Analysis
-  **Processed Dataset**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://drive.google.com/file/d/1JERZA9lDleHtfkWC2h-qoCpkggBR61-W/view?usp=sharing). 
- **Original Dataset**: [Kaggle - Credit Card Transactions Fraud Detection](https://www.kaggle.com/datasets/kartik2112/fraud-detection/data)
- **Status**: Completed
- **Tools Used**: Python, Pandas, Matplotlib, Seaborn, Scikit-learn, XGBoost
## :memo: Project Description
This project focuses on analyzing banking transactions to identify fraud patterns. It utilizes Exploratory Data Analysis (EDA) techniques and machine learning models to predict fraudulent transactions. The goal is to predict fraudulent transactions based on various features like transaction amount, time, and user information.
### :brain: Key Techniques Used
#### 1. Exploratory Data Analysis (EDA): 
- To understand the data and identify potential patterns of fraud.
#### 2. Logistic Regression: 
- For binary classification (fraud vs. non-fraud).
#### 3. Decision Trees: 
- A powerful model for classification tasks.
#### 4. Ensemble Learning: 
- Using multiple models to improve the performance and robustness of predictions. The following ensemble methods were used:
- **Bagging**: Involves training multiple instances of the same model on different subsets of the data and averaging the predictions. This reduces variance and helps avoid overfitting.
- **Boosting**: Combines multiple weak models (typically decision trees) to create a stronger model. It focuses on the mistakes made by previous models and gives more weight to difficult examples. **XGBoost**, a popular boosting algorithm, was used for this task due to its high performance.
- **Stacking**: Involves training different models and using another model (meta-model) to combine the predictions of these models to produce the final output. This method leverages the strengths of different models for better accuracy.
### :key: Key Steps
#### 1. Data Preprocessing:
- Cleaning and transforming the data for better model performance (handling missing values, feature engineering like extracting hour from timestamps, etc.).
#### 2. Modeling: 
- Building various classification models and comparing their accuracy.
#### 3. Evaluation:
- Comparing models based on key performance metrics:
- **Accuracy**: Overall correctness of the model.
- **Precision**: Correct positive predictions over total predicted positives.
- **Recall (Sensitivity)**: Correct positive predictions over total actual positives.
- **F1 Score**: Harmonic mean of precision and recall.
- **Confusion Matrix**: To visualize prediction errors.
- **ROC Curve and AUC (Area Under Curve)**: Evaluate model performance across different threshold values and handle imbalanced datasets effectively.
### :toolbox: Technologies Used
- **Python 3**
- **Pandas**: Data manipulation and analysis
- **Matplotlib & Seaborn**: Data visualization
- **Scikit-learn**: Machine learning modeling
- **XGBoost**: Gradient boosting for improved performance
- **Dash**: For building an interactive dashboard
- **Plotly**: Advanced data visualizations
### :rocket: Application Deployment
- Built an interactive dashboard using Dash (Python framework for web applications).
- Visualizes fraud patterns across different features.
- Graphs and summary tables included for easy analysis.
  
# Fraud Analysis Dashboard
## 🚀 Live Application
Access the deployed application: [Fraud Analysis Dashboard](https://fraud-analysis-dashboard-hiyr.onrender.com)
### :dart: Results
After training and evaluating the models, here are the performance metrics obtained:

| Modèle               | Recall (classe 1) | Précision (classe 1) | F1-score | AUC (ROC) |
|----------------------|-------------------|-----------------------|----------|-----------|
| Decision Tree        | 0.9650            | 0.9690                | 0.9670   | 0.9908    |
| Logistic Regression  | 0.8730            | 0.8880                | 0.8800   | 0.9600    |
| Random Forest        | 0.9675            | 0.9770                | 0.9722   | 0.9955    |
| Stacking             | 0.9640            | 0.9730                | 0.9685   | 0.9890    |
| AdaBoost             | 0.9400            | 0.9490                | 0.9445   | 0.9840    |
| Gradient Boosting    | 0.9745            | 0.9755                | 0.9750   | 0.9962    |
| XGBoost              | **0.9775**        | **0.9760**            | **0.9767** | **0.9974** |

### :mag: Key Observations
- **XGBoost** offers the best balance between fraud detection and low false alarms.  
- **Gradient Boosting** shows performance very close to XGBoost, with excellent sensitivity and precision.  
- **Random Forest** provides a good trade-off between accuracy and interpretability, suitable for regulated environments.  
- **Logistic Regression**, while interpretable, misses too many fraud cases (low recall) to be recommended in this high-risk context.

### :star2: Feature Importance (from XGBoost)
The most influential features for detecting fraud were:
- Transaction Amount (amt)
- Transaction Hour (hour)
- City Population (city_pop)
- Merchant Category (category)
- (Visuals like feature importance graphs can be added later)
