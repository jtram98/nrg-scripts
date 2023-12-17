from balance_checker import check_bal
import logger_config


logger_config.setup_logging()

def main():
    check_bal()

if __name__ == "__main__":
    main()
