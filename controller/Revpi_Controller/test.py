from revpi.data_provider import write_outputs


def main():

    print("START TEST")

    write_outputs({

        "BUZZ1": 0,
        "BUZZ2": 0,
        "BUZZ3": 0,

        "LED1": 0,
        "LED2": 0,
        "LED3": 0,
        "LED4": 0,
        "LED5": 0,
        "LED6": 0,
        "LED7": 0,
        "LED8": 0,

        "RELAY_MOTOR": 0,
        "RELAY_FAN": 0,
        "RELAY_LAMP": 0,

    })

    print("TEST FINISHED")


if __name__ == "__main__":
    main()