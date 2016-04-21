# -*- coding: utf-8 -*-


def readfile(name):
    """Leggi i contenuti di un file.
    :param name: Nome del file
    """
    file = open(name, 'r')
    content = file.read()
    file.close()
    return content


def writefile(name, content):
    """Scrivi qualcosa su un file, sovrascrivendo qualsiasi cosa ci sia al suo interno.
    :param name: Nome del file
    :param content: Contenuto del file
    """
    file = open(name, 'w')
    file.write(content)
    file.close()
