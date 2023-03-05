def repository_from_url(url: str) -> str:
    repository_name = ""

    if url.startswith("https"):
        repository_name = "/".join(url[0:-4].split("/")[-2:])
    elif url.startswith("git"):
        repository_name = url.split(":")[1][:-4]

    return repository_name
