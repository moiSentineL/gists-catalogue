import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import requests

try:
    # Import for normal execution
    from scripts.gist import Gist
except ImportError:
    # Import for testing context
    from gist import Gist

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# GitHub username and access token are defined as ENV variables
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "rjvitorino")
GITHUB_TOKEN = os.getenv("GISTMASTER_TOKEN")

# API Endpoint to retrieve Gists and Headers for authentication
GITHUB_API = f"https://api.github.com/users/{GITHUB_USERNAME}/gists"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

GIST_FORMAT = """

### [{heading}](gists/{folder_name}/index.md)

* **Description**: {description}
* **Language**: {language}
* **Created at**: {creation_date}
* **Last updated at**: {update_date}

"""


with open("scripts/readme", "r") as readmefile:
    README = readmefile.read()

# Functions that use Github API to fetch its data


def fetch_gists() -> List[Gist]:
    """
    Fetch the list of Gists for the user with username set in `GITHUB_USERNAME`.

    Returns:
        List[Gist]: A list of Gist objects.
    """
    try:
        response = requests.get(GITHUB_API, headers=HEADERS)
        response.raise_for_status()
        gists_data = response.json()
        return [Gist.from_dict(gist) for gist in gists_data]
    except requests.HTTPError as http_error:
        logging.error(f"HTTP error occurred: {http_error}")
        raise
    except Exception as error:
        logging.error(f"An error occurred: {error}")
        raise


def fetch_gist_content(raw_url: str) -> str:
    """
    Fetch the content of a Gist file.

    Args:
        raw_url (str): The raw URL of the gist file.

    Returns:
        response.text (str): The content of the gist file.
    """
    try:
        response = requests.get(raw_url)
        response.raise_for_status()
        return response.text
    except requests.HTTPError as http_error:
        logging.error(f"HTTP error occurred: {http_error}")
        raise
    except Exception as error:
        logging.error(f"An error occurred: {error}")
        raise


# Functions to manage the content within this repository


def format_date(date_text: str, date_format: str = "YYYY-MM-DD") -> str:
    """
    Format the date string.

    Args:
        date_text (str): The date string to format.
        date_format (str): The format to use (default: 'YYYY-MM-DD').

    Returns:
        str: The formatted date string.
    """
    format_mappings = {
        "YYYY-MM": "%Y-%m",
        "YYYY/MM": "%Y/%m",
        "YYYY/MM/DD": "%Y/%m/%d",
        "YYYY-MM-DD": "%Y-%m-%d",
        "YYYYMMDD": "%Y%m%d",
    }
    date_obj = datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%SZ")
    return date_obj.strftime(format_mappings.get(date_format))


def sanitise_folder_name(name: str) -> str:
    """
    Sanitise the folder name by removing file extensions, replacing spaces,
    and special characters. Limit name length to no more than 50 characters.

    Args:
        name (str): The name to sanitise.

    Returns:
        str: The sanitised folder name.
    """
    # Remove file extension
    name_without_extension = re.sub(r"\.[^.]+$", "", name)
    # Replace non-alphanumeric characters with underscores
    sanitised_name = re.sub(r"[^a-zA-Z0-9]", "_", name_without_extension)
    return sanitised_name[:50]  # Limit folder name length


def generate_folder_name(gist: Gist) -> str:
    """
    Generate a human-readable folder name for a gist.

    Args:
        gist (Gist): The Gist object.

    Returns:
        str: A human-readable folder name.
    """
    # Format the creation date
    date_part = format_date(gist.created_at, "YYYYMMDD")

    # Sanitize and concatenate all filenames
    filenames_part = "_".join(
        sanitise_folder_name(filename) for filename in gist.files.keys()
    )

    # Combine date, -gist-, and filenames
    return f"{date_part}-{filenames_part}-gist"


def save_gist_files(gist: Gist, folder_name: str = None) -> str:
    """
    Save the files of a Gist to the local file system.

    Args:
        gist (Gist): The Gist object.

    """
    if not folder_name:
        folder_name = generate_folder_name(gist)
    files_dir = Path("gists") / folder_name / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    for filename, fileinfo in gist.files.items():
        content = fetch_gist_content(fileinfo.raw_url)
        with open(files_dir / filename, "w") as file:
            file.write(content)
    return folder_name


def create_gist_index(gist: Gist) -> str:
    """
    Create or update the index.md file for a gist.

    Args:
        gist (Gist): The Gist object.

    Returns:
        folder_name (str): The folder name of the gist
    """
    folder_name = generate_folder_name(gist)
    gist_dir = Path("gists") / folder_name
    gist_dir.mkdir(parents=True, exist_ok=True)

    index_content = [
        f"# {folder_name}",
        "",
        f"**Gist file**: [{gist.html_url}]({gist.html_url})",
        "",
        f"**Description**: {gist.description}",
        "",
        *(
            f"## {filename}\n\n```{fileinfo.language}\n{fetch_gist_content(fileinfo.raw_url)}\n```"
            for filename, fileinfo in gist.files.items()
        ),
    ]

    with open(gist_dir / "index.md", "w") as index_file:
        index_file.write("\n".join(index_content))
    return folder_name


def update_readme(gists: List[Gist], use_table_format: bool = True) -> None:
    """
    Update the README.md file with the list of Gists.

    Args:
        gists (List[Gist]): A list of Gist objects.
    """
    github_profile = gists[0].owner
    readme_content = README.format(
        github_username=github_profile.get("login", GITHUB_USERNAME),
        github_url=github_profile.get("html_url", ""),
    )

    gists_entries = []
    for index, gist in enumerate(gists, start=1):
        description = gist.description
        folder_name = generate_folder_name(gist)
        created_at = format_date(gist.created_at)
        updated_at = format_date(gist.updated_at)
        languages = ", ".join(file.language for file in gist.files.values())
        list_entry = GIST_FORMAT.format(
            heading=f"Gist no. {index}",
            folder_name=folder_name,
            description=gist.description,
            language=languages,
            creation_date=created_at,
            update_date=updated_at,
        )
        gists_entries.append(
            [
                index,
                description,
                folder_name,
                languages,
                created_at,
                updated_at,
                list_entry,
            ]
        )

    # Generate content based on the format (table vs list)
    if use_table_format:
        df = pd.DataFrame(
            gists_entries,
            columns=[
                "Gist",
                "Description",
                "Folder name",
                "Language(s)",
                "Creation date",
                "Last updated",
                "Gist Entry",
            ],
        )
        df["Gist"] = df.apply(
            lambda row: f"[{row.name + 1}](gists/{row['Folder name']}/index.md)",
            axis=1,
        )
        # Generate Markdown table
        gists_content = df[
            ["Gist", "Description", "Language(s)", "Creation date", "Last updated"]
        ].to_markdown(index=False)
    else:
        # Generate list format with the list entry (GIST_FORMAT values)
        gists_content = "".join([entry[-1] for entry in gists_entries])

    # Combine all parts of the README content
    full_readme_content = readme_content + gists_content

    # Write the README file
    with open(Path("README.md"), "w") as readme_file:
        readme_file.write(full_readme_content)