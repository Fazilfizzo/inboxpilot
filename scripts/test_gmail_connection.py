from app.integrations.gmail.client import GmailClient


def main() -> None:
    gmail = GmailClient()

    profile = gmail.get_profile()

    print("\nGmail connection successful!")
    print(f"Email address: {profile.get('emailAddress')}")
    print(f"Total messages: {profile.get('messagesTotal')}")

    messages = gmail.list_messages(
        query="in:inbox",
        max_results=5,
    )

    print(f"\nRetrieved {len(messages)} message IDs.")

    for message in messages:
        print(f"Message ID: {message['id']}")

        full_message = gmail.get_message(message["id"])

        print(f"Thread ID: {full_message.get('threadId')}")
        print(f"Snippet: {full_message.get('snippet')}")
        print("-" * 40)


if __name__ == "__main__":
    main()