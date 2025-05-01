"""
    Compat for commandline use, __init__ needed for module and packaging,
    __main__ for local use
"""

if __name__ == "__main__":
    from finanztool import main
    main()
