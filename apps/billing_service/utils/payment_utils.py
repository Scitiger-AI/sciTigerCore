"""
支付相关工具
实现支付宝支付客户端及相关辅助函数
"""
import json
import rsa
import uuid
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest

logger = logging.getLogger('billing_service')


def test_private_key(private_key_content):
    """
    测试私钥是否可以被正确加载
    """
    try:
        # 确保输入是字符串
        if not isinstance(private_key_content, str):
            logger.error(f"私钥内容类型错误: {type(private_key_content)}")
            return False
            
        key = rsa.PrivateKey.load_pkcs1(private_key_content.encode('utf-8'), format='PEM')
        logger.debug("私钥加载成功")
        return True
    except Exception as e:
        logger.error(f"私钥加载失败: {str(e)}")
        return False


def format_private_key(private_key):
    """
    将私钥格式化为正确的 PEM 格式
    """
    try:
        # 移除现有的所有换行和空格
        key = ''.join(private_key.strip().split())
        # 每64个字符添加一个换行
        chunks = [key[i:i+64] for i in range(0, len(key), 64)]
        # 添加 PEM 头尾标记和换行
        formatted_key = "-----BEGIN RSA PRIVATE KEY-----\n" + \
                       '\n'.join(chunks) + \
                       "\n-----END RSA PRIVATE KEY-----"
        
        logger.debug(f"格式化后的私钥长度: {len(formatted_key)}")
        return formatted_key
        
    except Exception as e:
        logger.error(f"私钥格式化失败: {str(e)}")
        raise


def format_public_key(public_key):
    """
    格式化公钥为正确的 PEM 格式
    """
    # 移除现有的所有换行和空格
    key = ''.join(public_key.strip().split())
    # 每64个字符添加一个换行
    chunks = [key[i:i+64] for i in range(0, len(key), 64)]
    # 组装成正确的PEM格式
    formatted_key = "-----BEGIN PUBLIC KEY-----\n" + \
                   '\n'.join(chunks) + \
                   "\n-----END PUBLIC KEY-----"
    return formatted_key


def get_alipay_client():
    """
    获取支付宝客户端实例
    """
    try:
        # 确保设置中存在ALIPAY_CONFIG配置
        if not hasattr(settings, 'ALIPAY_CONFIG'):
            logger.error("未找到ALIPAY_CONFIG设置")
            raise ValueError("未找到ALIPAY_CONFIG设置")
            
        alipay_client_config = AlipayClientConfig()
        alipay_client_config.server_url = settings.ALIPAY_CONFIG.get('GATEWAY', 'https://openapi.alipay.com/gateway.do')
        alipay_client_config.app_id = settings.ALIPAY_CONFIG.get('APP_ID')
        alipay_client_config.format = 'json'
        alipay_client_config.charset = 'utf-8'
        alipay_client_config.sign_type = 'RSA2'
        
        # 处理私钥 - 支持文件路径或直接设置私钥内容
        app_private_key = settings.ALIPAY_CONFIG.get('APP_PRIVATE_KEY')
        if app_private_key.startswith('-----BEGIN'):
            # 直接使用配置的私钥内容
            formatted_private_key = format_private_key(app_private_key)
        else:
            # 从文件读取私钥
            try:
                with open(app_private_key, encoding='utf-8') as f:
                    private_key = f.read()
                    logger.debug(f"原始私钥长度: {len(private_key)}")
                    formatted_private_key = format_private_key(private_key)
            except Exception as e:
                logger.error(f"读取私钥文件失败: {str(e)}")
                raise
                
        alipay_client_config.app_private_key = formatted_private_key
        
        # 处理公钥 - 支持文件路径或直接设置公钥内容
        alipay_public_key = settings.ALIPAY_CONFIG.get('ALIPAY_PUBLIC_KEY')
        if alipay_public_key.startswith('-----BEGIN'):
            # 直接使用配置的公钥内容
            formatted_public_key = format_public_key(alipay_public_key)
        else:
            # 从文件读取公钥
            try:
                with open(alipay_public_key, encoding='utf-8') as f:
                    public_key = f.read()
                    formatted_public_key = format_public_key(public_key)
            except Exception as e:
                logger.error(f"读取公钥文件失败: {str(e)}")
                raise
                
        alipay_client_config.alipay_public_key = formatted_public_key

        logger.info("支付宝客户端配置完成")
        
        client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
        return client
    except Exception as e:
        logger.error(f"初始化支付宝客户端失败: {str(e)}", exc_info=True)
        raise


def create_alipay_trade_page_pay(order, return_url, notify_url):
    """
    创建支付宝支付请求
    
    :param order: Order对象
    :param return_url: 支付成功后跳转的URL
    :param notify_url: 支付结果异步通知URL
    :return: 支付链接
    """
    try:
        client = get_alipay_client()
        
        model = AlipayTradePagePayModel()
        model.out_trade_no = str(order.order_number)
        model.total_amount = str(float(order.amount))
        
        # 根据订单类型设置不同的支付主题
        if order.order_type == 'subscription':
            # 如果是订阅订单，尝试获取订阅信息
            try:
                subscription_id = order.callback_data.get('subscription_id')
                if subscription_id:
                    from apps.billing_service.models import Subscription, SubscriptionPlan
                    subscription = Subscription.objects.select_related('plan').get(id=subscription_id)
                    plan_name = subscription.plan.name
                    subscription_duration = dict(Subscription.BILLING_CYCLE_CHOICES).get(subscription.billing_cycle)
                    model.subject = f"{plan_name}会员-{subscription_duration}"
                    logger.info(f"从订阅ID获取会员信息成功: plan={plan_name}, duration={subscription_duration}")
                else:
                    model.subject = f"订阅付款-{order.title}"
            except Exception as e:
                logger.error(f"获取订阅信息失败: {str(e)}")
                model.subject = f"订阅付款-{order.title}"
        elif order.order_type == 'points':
            model.subject = f"{order.points}积分购买"
        else:
            model.subject = order.title
            
        model.product_code = "FAST_INSTANT_TRADE_PAY"

        logger.info(f"创建支付请求: order_number={model.out_trade_no}, amount={model.total_amount}, subject={model.subject}")
        logger.debug(f"支付模型参数: {model.__dict__}")

        request = AlipayTradePagePayRequest(biz_model=model)
        request.notify_url = notify_url
        request.return_url = return_url
        
        response = client.page_execute(request, http_method="GET")
        logger.info(f"支付请求创建成功")
        return response
    except Exception as e:
        logger.error(f"创建支付请求失败: {str(e)}", exc_info=True)
        raise


def query_trade_status(order_number):
    """
    查询订单支付状态，返回解析后的JSON对象
    
    :param order_number: 订单编号
    :return: 查询结果的字典
    """
    try:
        client = get_alipay_client()
        
        model = AlipayTradeQueryModel()
        model.out_trade_no = order_number
        
        logger.info(f"查询订单状态: order_number={order_number}")
        
        request = AlipayTradeQueryRequest(biz_model=model)
        response = client.execute(request)
        
        # 解析响应JSON
        response_dict = json.loads(response)
        logger.info(f"订单状态查询结果: {response_dict.get('alipay_trade_query_response', {}).get('trade_status', 'UNKNOWN')}")
        return response_dict
    except Exception as e:
        logger.error(f"查询订单状态失败: {str(e)}", exc_info=True)
        raise


def verify_alipay_callback(post_data, signature):
    """
    验证支付宝回调的签名是否合法
    
    :param post_data: 回调POST数据
    :param signature: 签名
    :return: 验证结果布尔值
    """
    try:
        # 此处需要实现支付宝回调签名验证逻辑
        # 待实现
        return True
    except Exception as e:
        logger.error(f"验证支付宝回调签名失败: {str(e)}")
        return False


def create_wechat_pay(order, return_url, notify_url):
    """
    创建微信支付请求（占位函数，暂不实现具体逻辑）
    
    :param order: Order对象
    :param return_url: 支付成功后跳转的URL
    :param notify_url: 支付结果异步通知URL
    :return: 支付链接或支付参数
    """
    # 这里仅创建占位函数，不实现具体逻辑
    logger.info(f"创建微信支付请求（暂未实现）: order_number={order.order_number}")
    return f"wechat_pay_url_placeholder?order_id={order.id}&timestamp={timezone.now().timestamp()}"


def query_wechat_pay_status(order_number):
    """
    查询微信支付状态（占位函数，暂不实现具体逻辑）
    
    :param order_number: 订单编号
    :return: 查询结果的字典
    """
    # 这里仅创建占位函数，不实现具体逻辑
    logger.info(f"查询微信支付状态（暂未实现）: order_number={order_number}")
    return {
        'status': 'not_implemented',
        'message': '微信支付接口暂未实现'
    }


def generate_order_number():
    """
    生成订单编号
    
    :return: 订单编号字符串
    """
    # 格式：当前日期+随机字符串，如：20230815-a1b2c3d4
    now = timezone.now()
    date_str = now.strftime('%Y%m%d')
    random_str = str(uuid.uuid4()).replace('-', '')[:8]
    return f"{date_str}-{random_str}" 