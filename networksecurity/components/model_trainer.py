## Basic libraries
import sys,os

## Exceptions and logging
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

## Input variables
from networksecurity.entity.artifact_entity import DataTransformationArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

## Output variables
from networksecurity.entity.artifact_entity import ModelTrainingArtifact

## Utility functions
from networksecurity.utils.main_utils.utils import save_obj,load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data,evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

## Importing ML Algo
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier,GradientBoostingClassifier,RandomForestClassifier

import mlflow
import joblib

## Track ml model remote
import dagshub
dagshub.init(repo_owner='octoprakhar', repo_name='networksecurity-project', mlflow=True)


class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig, data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def track_mlflow(self, best_model, classificationmetric):
        with mlflow.start_run():
            f1_score = classificationmetric.f1_score
            precision_score = classificationmetric.precision_score
            recall_score = classificationmetric.recall_score

            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision_score",precision_score)
            mlflow.log_metric("recall_score",recall_score)
            # mlflow.sklearn.log_model(best_model,"model")
            # Save model locally
            joblib.dump(best_model, "model.pkl")
            mlflow.log_artifact("model.pkl")
        
    def train_model(self,x_train,y_train, x_test,y_test):

        ## Initializing the models
        models = {
            "Random Forest": RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "AdaBoost": AdaBoostClassifier()
        }

        params={
            "Decision Tree": {
                'criterion':['gini', 'entropy', 'log_loss'],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Random Forest":{
                # 'criterion':['gini', 'entropy', 'log_loss'],
                
                # 'max_features':['sqrt','log2',None],
                'n_estimators': [8,16,32,128,256]
            },
            "Gradient Boosting":{
                # 'loss':['log_loss', 'exponential'],
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.85,0.9],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,64,128,256]
            }
            
        }

        model_report : dict = evaluate_models(x_train,y_train,x_test,y_test,models,params)

        ## To get best model score from dict
        best_model_score = max(sorted(model_report.values()))

        ## To get the best model name from dict
        best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]

        best_model = models[best_model_name]

        logging.info(f"Best model: {best_model_name} with score: {best_model_score}")

        y_train_pred = best_model.predict(x_train)
        y_test_pred = best_model.predict(x_test)

        classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)

        ## Track train experiments with the MLFLOW
        self.track_mlflow(best_model, classification_train_metric)

        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

        ## Track test experiments with the MLFLOW
        self.track_mlflow(best_model, classification_test_metric)

        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)

        network_model = NetworkModel(preprocessor=preprocessor,model=best_model)
        save_obj(self.model_trainer_config.trained_model_file_path,network_model)

        ## Model trainer artifact
        return ModelTrainingArtifact(
            trained_model_file_path= self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric,

        )
    



        

    def initiate_model_trainer(self) -> ModelTrainingArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            ## Load training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train,y_train,x_test,y_test = (
                train_arr[:,:-1],
                train_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1]
            )

            model_trainer_artifact = self.train_model(x_train,y_train,x_test,y_test)
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e,sys)