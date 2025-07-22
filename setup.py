from setuptools import setup, find_packages

setup(
    name="easy_custom_titlebar",
    version="0.1.1",  # <-- Change this to a new version!
    description="A reusable custom title bar and window manager for Pygame/Win32 apps, with bundled assets.",
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