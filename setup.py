from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="easy_custom_titlebar",
    version="2.0.0",  # Major release: complete overhaul, new features, and full documentation
    description="A reusable custom title bar and window manager for Pygame/Win32 apps, with bundled assets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Enazzzz",  # Update this with your actual name
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "easy_custom_titlebar": ["assets/*.png", "assets/*.ico"],
    },
    install_requires=[
        "pygame",
        "pywin32",
    ],
    python_requires=">=3.7",
) 