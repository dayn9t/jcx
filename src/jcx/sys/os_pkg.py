"""Operating system package management utilities.

This module provides utilities for comparing installed packages between
systems by parsing dpkg-style package list files.
"""

from pydantic import BaseModel


def parse_package_file(filename: str) -> set[str]:
    """Parse a dpkg-style package list file and return installed package names.

    The file format is expected to have lines with package name and status,
    separated by whitespace. Only packages with "install" status are included.

    Args:
        filename: Path to the package list file.

    Returns:
        Set of installed package names. Empty set if file doesn't exist.

    """
    installed_packages: set[str] = set()
    try:
        with open(filename, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts: list[str] = line.split()
                    if len(parts) >= 2:
                        package_name: str = parts[0]
                        status: str = parts[1]
                        if status == "install":
                            installed_packages.add(package_name)
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")
    return installed_packages


class PackagesDiff(BaseModel):
    """Model representing the difference between two package lists.

    Attributes:
        only_in_a: Packages installed in system A but not in system B.
        only_in_b: Packages installed in system B but not in system A.

    """

    only_in_a: set[str]
    only_in_b: set[str]

    def get_only_in_a_str(self) -> str:
        """Get packages only in A as a space-separated string.

        Returns:
            Space-separated string of sorted package names unique to A.

        """
        return " ".join(sorted(self.only_in_a))

    def get_only_in_b_str(self) -> str:
        """Get packages only in B as a space-separated string.

        Returns:
            Space-separated string of sorted package names unique to B.

        """
        return " ".join(sorted(self.only_in_b))


def compare_packages(file_a: str, file_b: str) -> PackagesDiff:
    """Compare two package list files and return the differences.

    Args:
        file_a: Path to the first package list file.
        file_b: Path to the second package list file.

    Returns:
        PackagesDiff containing packages unique to each file.

    """
    packages_a: set[str] = parse_package_file(file_a)
    packages_b: set[str] = parse_package_file(file_b)

    # a中安装但b中未安装的包
    return PackagesDiff(
        only_in_a=packages_a - packages_b, only_in_b=packages_b - packages_a
    )


if __name__ == "__main__":
    a_file = "a.txt"
    b_file = "b.txt"

    diff = compare_packages(a_file, b_file)

    print("a中安装的包,b中没有安装:", diff.get_only_in_a_str())
    print("b中安装的包,a中没有安装:", diff.get_only_in_b_str())

    # 203 上运行导致：systemd-timesyncd 被卸载
