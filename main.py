# import hrm
from modules import hrm

def main():
    # print HRM
    while True:
        hrm = getHRM()
        print(f"Heart Rate Data: {hrm}")

if __name__ == "__main__":
    main()
