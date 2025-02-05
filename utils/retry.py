import time
import random
import logging
import functools
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, Union
from datetime import datetime

from utils.logger import Logger

logger = Logger(__name__)

T = TypeVar('T')

class RetryError(Exception):

    """重试失败异常"""
    pass

def retry(
    max_tries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    jitter: bool = True,
    on_retry: Optional[Callable[[Exception, int], None]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    重试装饰器
    Args:
        max_tries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 退避系数（每次重试后延迟时间将乘以这个值）
        exceptions: 需要重试的异常类型
        jitter: 是否添加随机抖动
        on_retry: 重试回调函数
    Returns:
        装饰后的函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            tries = 0
            current_delay = delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    tries += 1
                    
                    if tries >= max_tries:
                        logger.error(
                            f"Maximum retries ({max_tries}) exceeded for {func.__name__}",
                            exc_info=True
                        )
                        raise RetryError(
                            f"Failed after {tries} tries. Last error: {str(e)}"
                        ) from e
                    
                    if on_retry:
                        on_retry(e, tries)
                    
                    # 计算下一次重试的延迟时间
                    sleep_time = current_delay
                    if jitter:
                        sleep_time *= (0.5 + random.random())
                    
                    logger.warning(
                        f"Retry {tries}/{max_tries} for {func.__name__} "
                        f"after {sleep_time:.2f}s"
                    )
                    
                    time.sleep(sleep_time)
                    current_delay *= backoff
                    
        return wrapper
    return decorator

class RetryWithTimeout:
    """带超时的重试装饰器类"""
    
    def __init__(
        self,
        timeout: float,
        max_tries: Optional[int] = None,
        delay: float = 1.0,
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
        on_retry: Optional[Callable[[Exception, int], None]] = None
    ):
        """
        初始化
        Args:
            timeout: 超时时间（秒）
            max_tries: 最大重试次数（如果为None，则由超时时间和延迟时间决定）
            delay: 重试延迟时间（秒）
            exceptions: 需要重试的异常类型
            on_retry: 重试回调函数
        """
        self.timeout = timeout
        self.max_tries = max_tries
        self.delay = delay
        self.exceptions = exceptions
        self.on_retry = on_retry

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time.time()
            tries = 0
            
            while True:
                try:
                    return func(*args, **kwargs)
                    
                except self.exceptions as e:
                    tries += 1
                    elapsed_time = time.time() - start_time
                    
                    # 检查是否超时或超过最大重试次数
                    if elapsed_time >= self.timeout or \
                       (self.max_tries and tries >= self.max_tries):
                        logger.error(
                            f"Retry failed for {func.__name__}: "
                            f"timeout={self.timeout}s, tries={tries}",
                            exc_info=True
                        )
                        raise RetryError(
                            f"Failed after {tries} tries ({elapsed_time:.2f}s). "
                            f"Last error: {str(e)}"
                        ) from e
                    
                    if self.on_retry:
                        self.on_retry(e, tries)
                    
                    # 确保不会超时
                    remaining = self.timeout - elapsed_time
                    if remaining <= 0:
                        raise RetryError(
                            f"Timeout exceeded ({self.timeout}s)"
                        )
                    
                    sleep_time = min(self.delay, remaining)
                    logger.warning(
                        f"Retry {tries} for {func.__name__} "
                        f"after {sleep_time:.2f}s"
                    )
                    time.sleep(sleep_time)
                    
        return wrapper

# 预定义的重试装饰器
retry_3_times = retry(max_tries=3)
retry_with_1min_timeout = RetryWithTimeout(timeout=60)
retry_network = retry(
    max_tries=5,
    delay=2.0,
    backoff=2.0,
    exceptions=(ConnectionError, TimeoutError)
)
