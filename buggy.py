def add(a, b):
    return a + b   # 修复：应为 a + b


def test():
    assert add(2, 3) == 5, "add 函数有 bug"
    print("测试通过")


if __name__ == "__main__":
    test()
