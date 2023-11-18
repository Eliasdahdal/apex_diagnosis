from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in apex_diagnosis/__init__.py
from apex_diagnosis import __version__ as version

setup(
	name="apex_diagnosis",
	version=version,
	description="It detects pneumonia and makes clinical diagnoses",
	author="Elias Dahdal",
	author_email="eliasdahdalwork@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
