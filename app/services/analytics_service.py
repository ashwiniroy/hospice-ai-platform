from app.services.dataset_service import DatasetService


class AnalyticsService:

    def __init__(self):
        self.dataset_service = DatasetService()

    def get_summary(self):
        df = self.dataset_service.load_hospice_dataset()

        return {
            "total_hospices": len(df),
            "total_states": df["state"].nunique(),
            "total_cities": df["city"].nunique(),
            "nonprofit_count": len(
                df[
                    df["proprietary_nonprofit"]
                    .fillna("")
                    .str.contains(
                        "nonprofit",
                        case=False,
                        regex=False
                    )
                ]
            )
        }

    def get_hospices_by_state(self):
        df = self.dataset_service.load_hospice_dataset()

        result = (
            df["state"]
            .dropna()
            .value_counts()
            .reset_index()
        )

        result.columns = [
            "state",
            "count"
        ]

        return result.to_dict(orient="records")

    def get_organization_types(self):
        df = self.dataset_service.load_hospice_dataset()

        result = (
            df["organization_type_structure"]
            .dropna()
            .value_counts()
            .reset_index()
        )

        result.columns = [
            "organization_type",
            "count"
        ]

        return result.to_dict(orient="records")