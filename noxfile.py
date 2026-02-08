import nox


@nox.session(python=["3.11", "3.12"])
def tests(session: nox.Session) -> None:
    session.install("-r", "requirements.txt")
    session.run("python", "-m", "pytest", "-q")
