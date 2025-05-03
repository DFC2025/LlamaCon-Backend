import os

from supabase import Client, create_client


class SupabaseClient:
    _client: Client = None

    @staticmethod
    def get_client(
        url: str = os.getenv("SUPABASE_URL"), key: str = os.getenv("SUPABASE_ANON_KEY")
    ) -> Client:
        if SupabaseClient._client is None:
            if not url or not key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables"
                )
            try:
                SupabaseClient._client = create_client(url, key)
            except Exception as e:
                raise RuntimeError("Failed to create Supabase client") from e
        return SupabaseClient._client


def get_supabase_client(
    url: str = os.getenv("SUPABASE_URL"), key: str = os.getenv("SUPABASE_ANON_KEY")
) -> Client:
    """
    Get the Supabase client instance.
    """
    client = SupabaseClient.get_client(url, key)
    return client
