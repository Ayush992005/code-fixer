from repair import repair

tests = {
    "c": '#include <stdio.h>\nint main() {\n    int x = 5\n    printf("%d\\n", x)\n    return 0;\n}\n',
    "python": 'print("hi"\nx = 5\n',
    "java": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("hi")\n    }\n}\n',
    "cpp": '#include <iostream>\nint main() {\n    std::cout << "hi" << std::endl\n    return 0;\n}\n',
}

for lang, code in tests.items():
    r = repair(code, lang)
    print(f"[{lang}] success={r['success']} attempts={r['attempts']}")
    print(r["fixed_code"])
