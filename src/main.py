"""
main.py

Main entry point of the UEBA project.

This script will execute the complete UEBA pipeline:

1. Load CERT r4.2 logs
2. Preprocess the data
3. Build behavioral features
4. Apply the rule-based scoring engine
5. Train and apply the Isolation Forest model
6. Calculate the final risk score
7. Generate UEBA alerts
8. Export alerts to CSV
9. Later: send alerts to Elasticsearch

The first version of this file will be completed after testing each module separately.
"""


def main():
    """
    Main function of the UEBA pipeline.
    """
    print("UEBA pipeline will be implemented step by step.")


if __name__ == "__main__":
    main()