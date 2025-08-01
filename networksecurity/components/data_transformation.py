import os, sys
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

## Dropping the target column
from networksecurity.constant.training_pipeline import TARGET_COLUMN

## Imputer parameters for KNN imputer
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS

## Importing validation artifact for input
from networksecurity.entity.artifact_entity import DataValidationArtifact

## Getting artifact entity in which I need to return 
from networksecurity.entity.artifact_entity import DataTransformationArtifact

## Configuration file
from networksecurity.entity.config_entity import DataTransformationConfig

## Logging and exception
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

## Getting utility functions
from networksecurity.utils.main_utils.utils import save_numpy_array_data,save_obj


class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationArtifact):
        try:
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
            self.data_transformation_config : DataTransformationConfig = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    
    ## Initializing KNN Imputer
    def get_data_transformer_object(cls)-> Pipeline:
        '''
        It initializes a KNNImputer object with the parameters specified in the training_pipeline.py file and 
        returns a Pipeline object with the KNNImputer object as the first step

        Args:
            cls: DataTransformation
        
        Returns:
            A Pipeline Object
        '''

        logging.info("Enter get_data_transformer_object method of transformation class")

        try:
            imputer:KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(
                f"Initialize KNNIMputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}"
            )
            processor: Pipeline = Pipeline([("imputer",imputer)])
            return processor
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        

    
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("Enter initiate_data_transformation method of DataTransformation class")
        try:
            logging.info("Starting data transformation")

            ## Read train and test data
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            ## Removing the target column
            ## Training dataframe
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1,0)
            ## Test dataframe
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1,0)

            ## Transforming data
            preprocessor = self.get_data_transformer_object()
            preprocessor_object  = preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)

            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            ## Save numpy array data
            save_numpy_array_data( self.data_transformation_config.transformed_train_file_path,array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path,array=test_arr)
            save_obj(self.data_transformation_config.transformed_object_file_path, preprocessor_object)

            ## Saving final preprocessor object. This can be saved anywhere in aws s3 bucket or local 
            save_obj("final_model/preprocessor.pkl",preprocessor_object)

            ## Preparing aritifacts
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path= self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )

            return data_transformation_artifact


        except Exception as e:
            raise NetworkSecurityException(e,sys)