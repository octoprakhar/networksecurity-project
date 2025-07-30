import sys

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig 

if __name__ == "__main__":
    try:
        trainingPipelineConfig = TrainingPipelineConfig()
        dataIngestionConfig = DataIngestionConfig(trainingPipelineConfig)
        dataValidationConfig = DataValidationConfig(training_pipeline_config=trainingPipelineConfig)
        data_ingestion = DataIngestion(dataIngestionConfig)

        logging.info("Initiate the data ingestion")

        dataIngestionArtifact = data_ingestion.initiate_data_ingestion()

        logging.info("Data initiation completed")
        print(dataIngestionArtifact)

        data_validation  = DataValidation(data_ingestion_artifact=dataIngestionArtifact, data_validation_config=dataValidationConfig)

        logging.info("initiate the data validation")
        
        dataValidationArtifact = data_validation.initiate_data_validation()

        logging.info("Data validation completed")
        print(dataValidationArtifact)
        
    except Exception as e:
        raise NetworkSecurityException(e,sys)