from typing import Optional, Iterable, List, Any, AnyStr, TextIO
from typing_extensions import Annotated
import requests
from requests.exceptions import ConnectionError
from http import HTTPStatus
from lxml import etree
import typer
from pprint import pprint
import sys

XPATH_TEXT_WITHOUT_SCRIPTS = etree.ETXPath("body//*[not(self::script)]/text()")

def write_matches(matches: Iterable, file: TextIO=sys.stdout) -> None:
    for match in matches:
        if (stripped := match.strip()):
            file.write(stripped)
            file.write('\n')
        


def main(link: str, file: Annotated[Optional[str], typer.Argument()] = None) -> None:
    # TODO: errors: bad link, bad response
    res: requests.Response = requests.get(link)
    match res.status_code:
        case HTTPStatus.BAD_REQUEST:
            raise Exception("Bad request")
        case HTTPStatus.NOT_FOUND:
            raise Exception("Not found")

    assert res.status_code == HTTPStatus.OK

    root = etree.HTML(res.text)
    matches: Iterable = XPATH_TEXT_WITHOUT_SCRIPTS(root) #type: ignore
    output = '\n'.join(matches)

    if file:
        with open(file, 'w') as file:
            write_matches(matches, file)
    else:
        write_matches(matches)
        # print(output)
    


if __name__ == "__main__":
    try:
        typer.run(main)
    except ConnectionError as e:
        print("Bad connection: probably a dnslookup error (host doesn't exist)")
