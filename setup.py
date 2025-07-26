from setuptools import find_packages, setup
from typing import List

def get_requirements()->List[str]:
    '''
    THis function will return list of requirements
    '''

    requirement_lst:List[str] = []

    try:
        with open('requirements.txt','r') as file:
            ## Read lines
            lines = file.readlines()
            for line in lines:
                requirement = line.strip()
                ## Ignore empty lines and -e .
                if requirement and requirement != '-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirement is not found")
    return requirement_lst

setup(
    name='NetworkSecurity',
    version="0.0.1",
    author="Prakhar Pathak",
    author_email="prakharpathak192@gmail.com",
    packages=find_packages(),
    install_requires = get_requirements()
)