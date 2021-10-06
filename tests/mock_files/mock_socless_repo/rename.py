import os
from pathlib import Path
import re, shutil, tempfile
import glob


def yesno(question):
    """Simple Yes/No Function."""
    prompt = f"{question} ? (y/n): "
    ans = input(prompt).strip().lower()
    if ans not in ["y", "n"]:
        print(f"{ans} is invalid, please try again...")
        return yesno(question)
    if ans == "y":
        return True
    return False


def sed_inplace(filename, pattern, repl):
    """
    Perform the pure-Python equivalent of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    https://stackoverflow.com/a/31499114/9866589
    """
    # For efficiency, precompile the passed regular expression.
    pattern_compiled = re.compile(pattern)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
        with open(filename) as src_file:
            for line in src_file:
                tmp_file.write(pattern_compiled.sub(repl, line))

    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)


# gather file paths eligible for string replacement
sep = os.path.sep
ignored_files = [
    f".{sep}package-lock.json",
    f".{sep}pyproject.toml",
    f".{sep}.gitignore",
    f".{sep}.coverage",
    f".{sep}setup.cfg",
    f".{sep}rename.py",
]
ignored_directories = [
    f".{sep}venv",
    f".{sep}node_modules",
    f".{sep}tox",
]
supported_extensions = [".txt", ".yml", ".py", ".json", ".yaml", ".md"]

file_paths = glob.glob(f".{sep}**", recursive=True)
filtered_files = [
    f_path
    for f_path in file_paths
    if Path(f_path).suffix in supported_extensions
    and f_path not in ignored_files
    and not any(f_path.startswith(dir_path) for dir_path in ignored_directories)
]


# get new repo integration name
new_integration_name = ""
confirmed = False
while not confirmed:
    print("What is the new integration name? (use - to separate words)")
    new_integration_name = input().strip().lower()
    new_integration_name = (
        new_integration_name.replace("socless-", "")
        .replace("socless", "")
        .replace("_", "-")
        .strip()
        .replace(" ", "-")
    )
    confirmed = yesno(f"New integration name: socless-{new_integration_name}")


# replace template names with new integration name
name_only_no_special_chars = new_integration_name.replace("-", "").lower()
name_only_with_underscores = new_integration_name.replace("-", "_").lower()
lowered_hyphens = f"socless-{new_integration_name}"
lowered_underscores = lowered_hyphens.replace("-", "_")
capitalized_spaces = " ".join(word.capitalize() for word in lowered_hyphens.split("-"))
camelcase = capitalized_spaces.replace(" ", "")
slash_separated = lowered_hyphens.replace("-", "_")

replacement_map = {
    "socless-template": lowered_hyphens,
    "socless_template": lowered_underscores,
    "Socless Template": capitalized_spaces,
    "SoclessTemplate": camelcase,
    "template": name_only_with_underscores,
}
for f_path in filtered_files:
    for searcher, replacement in replacement_map.items():
        sed_inplace(f_path, searcher, replacement)

# rename paths
paths_to_rename = [
    f".{sep}playbooks{sep}socless_template_integration_test",
    f".{sep}common_files{sep}template_helpers.py",
]

for full_path in paths_to_rename:
    new_name = full_path.replace("template", name_only_with_underscores)
    os.rename(full_path, new_name)
