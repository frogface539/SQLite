import logging

def get_logger(name):

    #creates or gets a logger named 'name'
    logger = logging.getLogger(name)

    #it prevents dupilicate log entries
    if not logger.handlers:
        handler = logging.StreamHandler() #this outputs logs to the console
        formatter = logging.Formatter('[%(levelname)s]  %(message)s') 
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG) #sets minimum log level

    return logger