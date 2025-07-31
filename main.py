import sys

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig 

if __name__ == "__main__":
    try:
        trainingPipelineConfig = TrainingPipelineConfig()
        dataIngestionConfig = DataIngestionConfig(trainingPipelineConfig)
        dataValidationConfig = DataValidationConfig(training_pipeline_config=trainingPipelineConfig)
        dataTransformationConfig = DataTransformationConfig(training_pipeline_config=trainingPipelineConfig)
        modelTrainerConfig = ModelTrainerConfig(training_pipeline_config=trainingPipelineConfig)
        
        
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

        logging.info("Data Transformation initiated")
        data_transformation = DataTransformation(data_validation_artifact=dataValidationArtifact,data_transformation_config=dataTransformationConfig)

        dataTransformationArtifact = data_transformation.initiate_data_transformation()
        logging.info("Data transformation completed")


        print(dataTransformationArtifact)

        logging.info("Model Training initiated")

        model_trainer = ModelTrainer(model_trainer_config=modelTrainerConfig,data_transformation_artifact=dataTransformationArtifact)
        modelTrainerArtifact = model_trainer.initiate_model_trainer()
        logging.info("Model training completed")
        print(modelTrainerArtifact)



        
    except Exception as e:
        raise NetworkSecurityException(e,sys)