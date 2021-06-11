from typing import Optional, Tuple, List

import cv2
import numpy as np
from pytesseract import pytesseract, Output
from PIL import Image

from mapadroid.ocr.screen_type import ScreenType
from mapadroid.utils.logging import get_origin_logger, LoggerEnums, get_logger

logger = get_logger(LoggerEnums.ocr)

screen_texts: dict = {1: ['Geburtdatum', 'birth.', 'naissance.', 'date'],
                      2: ['ZURUCKKEHRENDER', 'ZURÜCKKEHRENDER', 'GAME', 'FREAK', 'SPIELER'],
                      3: ['Google', 'Facebook'],
                      4: ['Benutzername', 'Passwort', 'Username', 'Password', 'DRESSEURS'],
                      5: ['Authentifizierung', 'fehlgeschlagen', 'Unable', 'authenticate',
                          'Authentification', 'Essaye'],
                      6: ['RETRY', 'TRY', 'DIFFERENT', 'ACCOUNT', 'ANDERES', 'KONTO', 'VERSUCHEN',
                          'AUTRE', 'AUTORISER'],
                      7: ['incorrect.', 'attempts', 'falsch.', 'gesperrt'],
                      8: ['Spieldaten', 'abgerufen', 'lecture', 'depuis', 'server', 'data'],
                      12: ['Events,', 'Benachrichtigungen', 'Einstellungen', 'events,', 'offers,',
                           'notifications', 'évenements,', 'evenements,', 'offres'],
                      14: ['kompatibel', 'compatible', 'OS', 'software', 'device', 'Gerät',
                           'Betriebssystem', 'logiciel'],
                      15: ['continuer...', 'aktualisieren?', 'now?', 'Aktualisieren', 'Aktualisieren,',
                           'aktualisieren', 'update', 'continue...', 'Veux-tu', 'Fais', 'continuer'],
                      16: ['modified', 'client', 'Strike', 'suspension', 'third-party',
                           'modifizierte', 'Verstoß', 'Sperrung', 'Drittpartei'],
                      17: ['Suspension', 'suspended', 'violating', 'days', ],
                      18: ['Termination', 'terminated', 'permanently'],
                      21: ['GPS', 'signal', 'GPS-Signal', '(11)', 'introuvable.',
                           'found.', 'gefunden.', 'Signal', 'geortet', 'detect', '(12)'],
                      23: ['CLUB', 'KIDS']}


def screendetection_get_type_internal(image,
                                        identifier) -> Optional[Tuple[ScreenType, Optional[dict], int, int, int]]:
    origin_logger = get_origin_logger(logger, origin=identifier)
    returntype: ScreenType = ScreenType.UNDEFINED
    globaldict: Optional[dict] = {}
    diff: int = 1
    origin_logger.debug("__screendetection_get_type_internal: Detecting screen type")

    texts = []
    try:
        with Image.open(image) as frame_org:
            width, height = frame_org.size

            origin_logger.debug("Screensize: W:{} x H:{}", width, height)

            if width < 1080:
                origin_logger.info('Resize screen ...')
                frame_org = frame_org.resize([int(2 * s) for s in frame_org.size], Image.ANTIALIAS)
                diff: int = 2

            texts = [frame_org]
            for thresh in [200, 175, 150]:
                fn = lambda x: 255 if x > thresh else 0  # noqa: E731
                frame = frame_org.convert('L').point(fn, mode='1')
                texts.append(frame)
            for text in texts:
                try:
                    globaldict = pytesseract.image_to_data(text, output_type=Output.DICT, timeout=40,
                                                           config='--dpi 70')
                except Exception as e:
                    origin_logger.error("Tesseract Error: {}. Exception: {}", globaldict, e)
                    globaldict = None
                origin_logger.debug("Screentext: {}", globaldict)
                if globaldict is None or 'text' not in globaldict:
                    continue
                n_boxes = len(globaldict['text'])
                for index in range(n_boxes):
                    if returntype != ScreenType.UNDEFINED:
                        break
                    if len(globaldict['text'][index]) > 3:
                        for screen_elem in screen_texts:
                            heightlimit = 0 if screen_elem == 21 else height / 4
                            if globaldict['top'][index] > heightlimit and globaldict['text'][index] in \
                                    screen_texts[screen_elem]:
                                returntype = ScreenType(screen_elem)
                if returntype != ScreenType.UNDEFINED:
                    break

            del texts
            frame.close()
    except (FileNotFoundError, ValueError) as e:
        origin_logger.error("Failed opening image {} with exception {}", image, e)
        return None

    return returntype, globaldict, width, height, diff


def check_pogo_mainscreen(filename, identifier):
    origin_logger = get_origin_logger(logger, origin=identifier)
    origin_logger.debug("__internal_check_pogo_mainscreen: Checking close except nearby with: file {}", filename)
    mainscreen = 0
    try:
        screenshot_read = cv2.imread(filename)
    except Exception:
        origin_logger.error("Screenshot corrupted")
        logger.debug("__internal_check_pogo_mainscreen: Screenshot corrupted...")
        return False
    if screenshot_read is None:
        origin_logger.error("__internal_check_pogo_mainscreen: Screenshot corrupted")
        return False

    height, width, _ = screenshot_read.shape
    gray = screenshot_read[int(height) - int(round(height / 5)):int(height),
                           0: int(int(width) / 4)]
    _, width_, _ = gray.shape
    radius_min = int((width / float(6.8) - 3) / 2)
    radius_max = int((width / float(6) + 3) / 2)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.Canny(gray, 200, 50, apertureSize=3)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, width / 8, param1=100, param2=15,
                               minRadius=radius_min,
                               maxRadius=radius_max)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (pos_x, _, _) in circles:
            if pos_x < width_ - width_ / 3:
                mainscreen += 1

    if mainscreen > 0:
        origin_logger.debug("Found avatar.")
        return True
    return False


def most_frequent_colour_internal(image, identifier) -> Optional[List[int]]:
    origin_logger = get_origin_logger(logger, origin=identifier)
    origin_logger.debug("most_frequent_colour_internal: Reading screen text")
    try:
        with Image.open(image) as img:
            w, h = img.size
            pixels = img.getcolors(w * h)
            most_frequent_pixel = pixels[0]

            for count, colour in pixels:
                if count > most_frequent_pixel[0]:
                    most_frequent_pixel = (count, colour)

            origin_logger.debug("Most frequent pixel on screen: {}", most_frequent_pixel[1])
    except (FileNotFoundError, ValueError) as e:
        origin_logger.error("Failed opening image {} with exception {}", image, e)
        return None

    return most_frequent_pixel[1]


def get_screen_text(screenpath: str, identifier) -> Optional[dict]:
    origin_logger = get_origin_logger(logger, origin=identifier)
    returning_dict: Optional[dict] = {}
    origin_logger.debug("get_screen_text: Reading screen text")

    try:
        with Image.open(screenpath) as frame:
            frame = frame.convert('LA')
            try:
                returning_dict = pytesseract.image_to_data(frame, output_type=Output.DICT, timeout=40,
                                                           config='--dpi 70')
            except Exception as e:
                origin_logger.error("Tesseract Error: {}. Exception: {}", returning_dict, e)
                returning_dict = None
    except (FileNotFoundError, ValueError) as e:
        origin_logger.error("Failed opening image {} with exception {}", screenpath, e)
        return None

    if isinstance(returning_dict, dict):
        return returning_dict
    else:
        origin_logger.warning("Could not read text in image: {}", returning_dict)
        return None


def get_inventory_text(temp_dir_path: str, filename, identifier, x1, x2, y1, y2) -> Optional[str]:
    origin_logger = get_origin_logger(logger, origin=identifier)
    screenshot_read = cv2.imread(filename)
    temp_path_item = temp_dir_path + "/" + str(identifier) + "_inventory.png"
    height = x1 - x2
    width = y1 - y2
    gray = cv2.cvtColor(screenshot_read, cv2.COLOR_BGR2GRAY)
    gray = gray[int(y2):(int(y2) + int(width)), int(x2):(int(x2) + int(height))]
    scale_percent = 200  # percent of original size
    scaled_width = int(gray.shape[1] * scale_percent / 100)
    scaled_height = int(gray.shape[0] * scale_percent / 100)
    dim = (scaled_width, scaled_height)

    # resize image
    gray = cv2.resize(gray, dim, interpolation=cv2.INTER_AREA)
    imwrite_status = cv2.imwrite(temp_path_item, gray)
    if not imwrite_status:
        origin_logger.error("Could not save file: {} - check permissions and path", temp_path_item)
        return None
    try:
        with Image.open(temp_path_item) as im:
            try:
                text = pytesseract.image_to_string(im)
            except Exception as e:
                origin_logger.error("Error running tesseract on inventory text: {}", e)
                return None
    except (FileNotFoundError, ValueError) as e:
        origin_logger.error("Failed opening image {} with exception {}", temp_path_item, e)
        return None
    return text