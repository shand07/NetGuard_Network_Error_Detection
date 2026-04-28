
from repositories.db import migrate
from repositories.endpoint_repository import EndpointRepository
from models.endpoint import Endpoint


def main():
    migrate()

    repo = EndpointRepository()

    # Optional: only add a default endpoint if the database is empty
    if not repo.list_all():
        repo.add(Endpoint(
            id=None,
            name="Google",
            url="https://google.com"
        ))

    print("NetGuard initialized successfully.")

if __name__ == "__main__":
    main()
