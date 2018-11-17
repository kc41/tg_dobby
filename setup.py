import os
import setuptools


class CleanCommand(setuptools.Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    # noinspection PyMethodMayBeStatic
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


setuptools.setup(
    name="tg_dobby",

    python_requires="==3.6.*",

    author="Konstantin Chupin",
    author_email="kchupin41@gmail.com",
    description="Telegram Dobby",

    install_requires=[
        "aiohttp==3.4.4",
        "aiotg==0.9.9",
        "aioredis==1.1.0",
        "PyYAML==3.13",
        "pydantic==0.14",
        "yargy==0.11.0",

        # TODO FIX: move to build dependencies
        "parameterized",
        "transliterate==1.10.2",
    ],

    packages=setuptools.find_packages(exclude=("tests",)),

    classifiers=['Private :: Do Not Upload'],

    cmdclass={
        'clean': CleanCommand,
    }
)
