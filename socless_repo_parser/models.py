# from pydantic import Field
import ast
import json
import os
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pydantic import BaseModel
from github.Repository import Repository
from github.ContentFile import ContentFile
from socless_repo_parser.constants import INTERACTION_ARG_NAMES
import docstring_parser


@dataclass
class RepoMetadata:
    name: str
    org: str
    url: str = ""

    def get_full_name(self) -> str:
        """For use in pygithub's get_repo()"""
        return f"{self.org}/{self.name}"


@dataclass
class FileExistence:
    gh_repo: Repository
    file_path: str
    branch_exists: bool = False
    file_exists: bool = False
    file_contents: Union[bool, ContentFile, List[ContentFile]] = False


class SoclessFunctionMeta(BaseModel):
    lambda_folder_name: str = ""  # check_user_in_channel,
    deployed_lambda_name: str = ""  # socless_slack_check_user_in_channel,
    serverless_lambda_name: str = ""  # CheckIfUserInChannel
    supported_in_playbook: bool = True

    def check_supported_in_playbook_via_meta(self) -> bool:
        """Does not check function body if it has `handle_state`."""
        if not all(
            [
                self.deployed_lambda_name,
                self.lambda_folder_name,
                self.serverless_lambda_name,
            ]
        ):
            raise Exception(
                "SoclessFunctionMeta names must be populated to check if supported in playbook"
            )

        is_supported = True
        if self.lambda_folder_name.startswith("_"):
            is_supported = False
        if "endpoint" in self.lambda_folder_name:
            is_supported = False

        self.supported_in_playbook = is_supported
        return is_supported


# class SliceType(BaseModel):
#     type_name: str
#     items: List[str]

#     def __repr__(self) -> str:
#         items_as_string = ""
#         for i, item in enumerate(self.items):
#             if i == 0:
#                 items_as_string += f"{item}"
#             else:
#                 items_as_string += f",{item}"
#         return f"{self.type_name}<{items_as_string}>"

#     def __eq__(self, o: object) -> bool:
#         return str(self) == str(o)


# class ArrayType(SliceType):
#     type_name: str = "array"
#     items: List[Union[str, SliceType]]


# class UnionType(SliceType):
#     type_name = "union"
#     items: List[Union[str, ArrayType]]


class JsonDataType(str, Enum):
    STRING = "string"
    BOOLEAN = "boolean"
    NUMBER = "number"
    OBJECT = "object"
    NULL = "null"
    ARRAY = "array<>"
    UNION = "union<>"
    ANY = "any"


class SoclessFunctionArgument(BaseModel):
    """Data about an argument in `handle_state()`.

    `data_type` : `JsonDataType` Enum - `"string"|"number"|"boolean"|"object"|"array<>"|"array<data_type>"|"null"`
        If a type hint or default value is specified, what (JSON) data type is it.
    `required` : True if this argument does NOT have a default value.
    `description` : # TODO: Not yet implemented.
    `placeholder` : # TODO: Not fully implemented,
        but `placeholder` is currently populated with the default_value (if default_value is not empty)
    `internal` : # Custom field for marking args not used in `playbook.json`, such as `context`. TODO: Needs better logic
    `default_value` : # The default value for a given arg (if provided.) Ex: def myfn(my_arg: str = "a default")
    ```
    """

    name: str = ""
    data_type: Union[JsonDataType, str] = JsonDataType.NULL
    required: bool = False
    description: str = ""
    placeholder: Any = ""
    internal: bool = False
    default_value: Optional[Any]


class SoclessResourceType(str, Enum):
    SOCLESS_TASK = "socless_task"
    SOCLESS_INTERACTION = "socless_interaction"


class SoclessFunction(BaseModel):
    meta: SoclessFunctionMeta = SoclessFunctionMeta()
    resource_type: SoclessResourceType = SoclessResourceType.SOCLESS_TASK
    description: str = ""
    arguments: List[SoclessFunctionArgument] = []
    supports_kwargs: bool = False
    return_statements: List[Dict[str, Any]] = []

    def check_and_set_resource_type(self):
        for arg in self.arguments:
            if arg.name in INTERACTION_ARG_NAMES:
                self.resource_type = SoclessResourceType.SOCLESS_INTERACTION

    def check_and_set_supported_in_playbook(self):
        # requires that function meta is populated
        return self.meta.check_supported_in_playbook_via_meta()

    def parse_docstring_and_set_descriptions(self, handle_state_node: ast.FunctionDef):
        """Get docstring info from fn node and populate fn description and arg descriptions. NOTE: call this after self.arguments have been populated."""
        docstring = ast.get_docstring(handle_state_node, clean=False)
        if not docstring:
            return

        parsed_docstring = docstring_parser.parse(docstring)
        self.description = parsed_docstring.short_description or ""
        # print(parsed_docstring.long_description)  # anything after the first sentence

        for param in parsed_docstring.params:
            for arg in self.arguments:
                if arg.name == param.arg_name.strip():
                    arg.description = param.description
                    break  # only breaks inner `arg` loop


class IntegrationMeta(BaseModel):
    repo_url: str = ""
    integration_family: str = ""


class IntegrationFamily(BaseModel):
    meta: IntegrationMeta = IntegrationMeta()
    functions: List[SoclessFunction] = []

    def fill_missing_arg_descriptions(self):
        """Fill missing arg descriptions by searching if any other function in this family has the same arg filled out."""
        if not self.functions:
            raise Exception(
                "No functions to fill, run this after functions have been parsed."
            )

        # get all descriptions
        description_map = {}
        for fn in self.functions:
            for arg in fn.arguments:
                if arg.description:
                    description_map[arg.name] = arg.description

        # fill missing descriptions
        for fn in self.functions:
            for arg in fn.arguments:
                if not arg.description and arg.name in description_map:
                    arg.description = description_map[arg.name]


class AllIntegrations(BaseModel):
    integrations: List[IntegrationFamily] = []

    def write_info_to_file(self, file_path: str = "socless_info"):
        root, ext = os.path.splitext(file_path)
        ext = ext if ext else ".json"
        with open(f"{root}{ext}", "w") as f:
            f.write(json.dumps(self.dict(), indent=4))


def build_integration_classes_from_json(input: Union[str, dict]) -> AllIntegrations:
    if isinstance(input, str):
        input = json.loads(input)

    all_integrations = []

    for integration_family in input["integrations"]:
        all_integrations.append(IntegrationFamily(**integration_family))

    output = AllIntegrations(integrations=all_integrations)

    return output
