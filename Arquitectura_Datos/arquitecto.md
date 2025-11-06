graph LR
    subgraph Data Sources
        DB[Base de Datos Relacional: Usuarios]
        API[API: Catálogo, Redes Sociales]
        LOGS[Logs/Eventos de Interacción]
    end

    subgraph Data Ingestion
        KAFKA[Apache Kafka: Ingesta en Tiempo Real]
        SPARK_E[Apache Spark (Batch ETL)]
    end

    subgraph Data Lake (Storage & Catalog)
        S3_LZ(S3: Landing Zone - Crudo)
        S3_RZ(S3: Raw Zone - Particionado)
        S3_CZ(S3: Processed Zone - Parquet)
        GLUE_CAT[AWS Glue Data Catalog]
    end

    subgraph Data Processing & Query
        SPARK_P[Apache Spark (Procesamiento/ML)]
        ATHENA[AWS Athena (Consultas SQL en S3)]
    end

    subgraph Business Needs
        ML[Machine Learning: Motor de Recomendaciones]
        BI[BI Tools / Dashboards]
        ALERTS[Alertas en Tiempo Real (Fallo de Reproducción)]
    end

    DB --> SPARK_E
    API --> SPARK_E
    LOGS --> KAFKA

    SPARK_E --> S3_LZ
    KAFKA --> S3_LZ

    S3_LZ --> SPARK_P
    S3_RZ --> SPARK_P
    SPARK_P --> S3_CZ
    S3_CZ --> GLUE_CAT

    S3_CZ & GLUE_CAT --> ATHENA
    S3_CZ & GLUE_CAT --> SPARK_P

    ATHENA --> BI
    SPARK_P --> ML
    KAFKA --> ALERTS