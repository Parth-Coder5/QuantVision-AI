from typing import Any

import numpy as np

def MA(real: np.ndarray, timeperiod: int = 30) -> np.ndarray: ...
def RSI(real: np.ndarray, timeperiod: int = 14) -> np.ndarray: ...
def MACD(
    real: np.ndarray,
    fastperiod: int = 12,
    slowperiod: int = 26,
    signalperiod: int = 9,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...
def BBANDS(
    real: np.ndarray,
    timeperiod: int = 5,
    nbdevup: float = 2.0,
    nbdevdn: float = 2.0,
    matype: int = 0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...

__version__: str
