from pydantic_settings import BaseSettings


class AppConfiguration(BaseSettings):
    app_name: str | None = None
    app_version: str | None = None
    s3_bucket: str | None = None
    s3_path: str | None = None
    aws_region: str = "sa-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_endpoint: str | None = None

    @property
    def s3_file_path(self) -> str:
        return f"s3://{self.s3_bucket}/{self.s3_path}"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }
