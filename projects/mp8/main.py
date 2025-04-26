# The goal of this machine project is to build a classifier that, given user and log data, can predict whether those users will be interested in our product.
import pandas as pd
import numpy as np

# imports necessary for building classifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import PolynomialFeatures
# from sklearn.preprocessing import StandardScaler

# Load datasets

# Write my classifier as a class called UserPredictor.
class UserPredictor():
    def __init__(self):
        self.pipeline = Pipeline([('lgm', LogisticRegression())])
        

    def fit(self,train_users,train_logs,train_y):
        """
        Fit the model on the training data.
        Merges user, logs, and target data to create the training set.
        
        train_users: DataFrame with user data (e.g., user_id, demographics).
        train_logs: DataFrame with log data (e.g., user actions, interactions).
        train_y: DataFrame with target values (e.g., whether the user is interested).
        """
        # Merge datasets on 'user_id' to create a single training dataset
        train_data = (train_users.merge(train_logs, how='inner', on='user_id'))
        train_data = train_data.merge(train_y, how='inner', on='user_id')
        
        # Assuming 'past_purchase_amt' is a feature (this might be changed later).
        X = train_data[['past_purchase_amt']]  
        # Assuming 'y' is the target column
        y = train_data['y'] 
        
        # Fit the model
        self.pipeline.fit(X, y)
    
    
    def predict(self,test_users,test_logs):
        """
        Predict user interest on the test dataset.
        
        test_users: DataFrame of user information for prediction.
        test_logs: DataFrame of user logs for prediction.
        
        Returns: Predicted labels for the test dataset.
        """
        # Merge test data
        test_data = test_users.merge(test_logs, how='inner', on='user_id')
    
        # Define features for prediction
        X_test = test_data[['past_purchase_amt']]  # Assuming same feature 'past_purchase_amt'
        
        # Make predictions
        predictions = self.pipeline.predict(X_test)
        
        return predictions
    
if __name__ == "__main__":
    main()