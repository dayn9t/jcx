from pydantic import BaseModel


def parse_package_file(filename: str) -> set[str]:
    """解析包列表文件，返回已安装的包名集合"""
    installed_packages: set[str] = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts: list[str] = line.split()
                    if len(parts) >= 2:
                        package_name: str = parts[0]
                        status: str = parts[1]
                        if status == 'install':
                            installed_packages.add(package_name)
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")
    return installed_packages

class PackagesDiff(BaseModel):
    """包差异模型"""
    only_in_a: set[str]
    only_in_b: set[str]

    def get_only_in_a_str(self) -> str:
        """获取仅在a中存在的包，格式化为字符串"""
        return ' '.join(sorted(self.only_in_a))

    def get_only_in_b_str(self) -> str:
        """获取仅在b中存在的包，格式化为字符串"""
        return ' '.join(sorted(self.only_in_b))

def compare_packages(file_a: str, file_b: str) -> PackagesDiff:
    """比较两个包列表文件"""
    packages_a: set[str] = parse_package_file(file_a)
    packages_b: set[str] = parse_package_file(file_b)

    # a中安装但b中未安装的包
    return PackagesDiff(
        only_in_a=packages_a - packages_b,
        only_in_b=packages_b - packages_a
    )




if __name__ == "__main__":
    a_file = 'a.txt'
    b_file = 'b.txt'

    diff = compare_packages(a_file, b_file)

    print("a中安装的包,b中没有安装:", diff.get_only_in_a_str())
    print("b中安装的包,a中没有安装:", diff.get_only_in_b_str())

    # 203 上运行导致：systemd-timesyncd 被卸载
