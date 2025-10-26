from setuptools import setup, find_packages

setup(
    name="ielts-master-platform",
    version="2.1.1",
    description="AI-powered IELTS writing assessment platform",
    packages=find_packages(),
    install_requires=[
        # Dependencies will be installed from backend/requirements.txt
    ],
    python_requires=">=3.11",
)


