"""
elastic_connector.py

This file contains functions used to send UEBA alerts to Elasticsearch.

Responsibilities:
- connect to Elasticsearch
- create or reset the UEBA alerts index
- convert pandas rows into Elasticsearch documents
- bulk index generated alerts

Elasticsearch is used as the storage layer for Grafana dashboards.
"""

from typing import Dict

import pandas as pd
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError as ElasticsearchConnectionError

from src.config import ELASTICSEARCH_HOST, ELASTICSEARCH_INDEX


def get_elasticsearch_client() -> Elasticsearch:
    """
    Create and return an Elasticsearch client.
    """
    return Elasticsearch(
        ELASTICSEARCH_HOST,
        request_timeout=60,
    )


def check_elasticsearch_connection(client: Elasticsearch) -> bool:
    """
    Check if Elasticsearch is reachable.

    We use client.info() instead of client.ping() because ping can return False
    in some local Docker configurations even when Elasticsearch is reachable.
    """
    try:
        info = client.info()
        print(
            f"Connected to Elasticsearch "
            f"{info['version']['number']} "
            f"on cluster '{info['cluster_name']}'."
        )
        return True
    except ElasticsearchConnectionError as error:
        print(f"Elasticsearch connection error: {error}")
        return False
    except Exception as error:
        print(f"Unexpected Elasticsearch error: {error}")
        return False


def reset_index(client: Elasticsearch, index_name: str = ELASTICSEARCH_INDEX) -> None:
    """
    Delete the index if it exists, then create it again.

    This is useful during development to avoid duplicate alerts.
    """
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)

    client.indices.create(index=index_name)


def clean_document(document: Dict) -> Dict:
    """
    Convert non-serializable values into Elasticsearch-compatible values.

    This function is especially useful for dates and pandas/numpy types.
    """
    cleaned = {}

    for key, value in document.items():
        if pd.isna(value):
            cleaned[key] = None
        elif hasattr(value, "isoformat"):
            cleaned[key] = value.isoformat()
        else:
            cleaned[key] = value

    return cleaned


def dataframe_to_actions(
    df: pd.DataFrame,
    index_name: str = ELASTICSEARCH_INDEX,
):
    """
    Convert a DataFrame into Elasticsearch bulk actions.
    """
    for _, row in df.iterrows():
        document = clean_document(row.to_dict())

        yield {
            "_index": index_name,
            "_source": document,
        }


def send_alerts_to_elasticsearch(
    alerts_df: pd.DataFrame,
    reset: bool = True,
    index_name: str = ELASTICSEARCH_INDEX,
) -> None:
    """
    Send UEBA alerts to Elasticsearch.

    Parameters:
        alerts_df: DataFrame containing UEBA alerts
        reset: if True, delete and recreate the index before inserting data
        index_name: Elasticsearch index name
    """
    client = get_elasticsearch_client()

    if not check_elasticsearch_connection(client):
        raise ConnectionError(
            f"Cannot connect to Elasticsearch at {ELASTICSEARCH_HOST}"
        )

    if reset:
        reset_index(client, index_name=index_name)

    actions = dataframe_to_actions(alerts_df, index_name=index_name)
    helpers.bulk(client, actions)

    print(f"Successfully indexed {len(alerts_df)} alerts into '{index_name}'.")