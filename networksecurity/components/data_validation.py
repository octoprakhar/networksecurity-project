from networksecurity.entity.artifact_entity import DataIngestionArtifact ## This will be input to data validation
from networksecurity.entity.artifact_entity import DataValidationArtifact ## This will be the output of data validation process

## All important variables regarding data validation process
from networksecurity.entity.config_entity import DataValidationConfig

## Getting the schema to compare it in this component
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
## Reading the schema
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file


## Exception and logs
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

## External libraries
from scipy.stats import ks_2samp # Check for data drift
import pandas as pd
import os,sys


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_cofig = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def validate_number_of_columns(self,dataframe:pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self._schema_cofig)
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Data frame has columns : {len(dataframe.columns)}")

            if len(dataframe.columns) == number_of_columns:
                return True
            else:
                return False

        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def validate_numerical_columns(self, dataframe:pd.DataFrame) -> bool:
        try:
            numerical_features = [feature for feature in dataframe.columns if dataframe[feature].dtype != 'O']
            if len(numerical_features) != 0:
                return True
            else:
                return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold=0.05) -> bool:
        try:
            status = True  # Assume no drift unless we detect one
            report = {}

            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2)

                drift_detected = is_same_dist.pvalue < threshold  # drift if p-value < threshold
                if drift_detected:
                    status = False  # Drift found in at least one column

                report[column] = {
                    "p_value": float(is_same_dist.pvalue),
                    "drift_status": bool(drift_detected)
                }

            drift_report_file_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

        
        
    def initiate_data_validation(self)-> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            ## Read data from train and test
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path )

            ## Validate number of columns
            status = self.validate_number_of_columns(train_dataframe)
            error_message= ""
            if not status:
                error_message = "Train dataframe doesn't contain all columns \n"
            status = self.validate_number_of_columns(test_dataframe)
            if not status:
                error_message = "Test dataframe doesn't contain all columns \n"

            ## vaidate is numerical columns exists or not
            status = self.validate_numerical_columns(train_dataframe)
            if not status:
                error_message = "Train dataframe doesn't contain numerical columns \n"
            status = self.validate_numerical_columns(test_dataframe)
            if not status:
                error_message = "Test dataframe doesn't contain numerical columns \n"
            

            ## Let's check datadrift
            status = self.detect_dataset_drift(base_df=train_dataframe, current_df=test_dataframe)
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path,index=False, header=True,

            )

            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path,index=False, header=True,
                
            )

            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path= self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path= self.data_validation_config.drift_report_file_path
            )

            return data_validation_artifact

    


        except Exception as e:
            raise NetworkSecurityException(e,sys)

