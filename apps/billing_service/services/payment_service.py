"""
支付服务
实现支付相关的业务逻辑
"""

import logging
import json
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.db import transaction

from apps.billing_service.models import Order, Payment, PaymentGatewayConfig
from apps.billing_service.utils.payment_utils import (
    create_alipay_trade_page_pay,
    create_wechat_pay,
    query_trade_status,
    generate_order_number
)

logger = logging.getLogger('billing_service')


class PaymentService:
    """
    支付服务类
    
    提供支付相关的业务逻辑
    """
    
    @staticmethod
    def create_order(tenant, user, order_type, amount, title, description=None, points=0, 
                     discount_amount=0, tax_amount=0, currency='CNY', callback_data=None, 
                     created_by=None, ip_address=None, user_agent=None):
        """
        创建订单
        
        Args:
            tenant: 租户对象
            user: 用户对象
            order_type: 订单类型，如 'subscription', 'points' 等
            amount: 订单金额
            title: 订单标题
            description: 订单描述
            points: 积分数量（如果是积分订单）
            discount_amount: 折扣金额
            tax_amount: 税费
            currency: 货币
            callback_data: 回调数据
            created_by: 创建者
            ip_address: IP地址
            user_agent: 用户代理
            
        Returns:
            Order: 创建的订单对象
        """
        try:
            order = Order.objects.create(
                tenant=tenant,
                user=user,
                order_type=order_type,
                amount=amount,
                title=title,
                description=description,
                points=points,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                currency=currency,
                callback_data=callback_data or {},
                created_by=created_by or user,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            logger.info(f"订单创建成功: order_id={order.id}, order_number={order.order_number}")
            return order
            
        except Exception as e:
            logger.error(f"创建订单失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def create_payment(order, payment_method, payment_gateway=None, return_url=None, notify_url=None, 
                       ip_address=None, user_agent=None):
        """
        创建支付记录并生成支付链接
        
        Args:
            order: 订单对象
            payment_method: 支付方式，如 'alipay', 'wechat' 等
            payment_gateway: 支付网关，如果为None则使用默认网关
            return_url: 支付成功后跳转的URL
            notify_url: 支付结果异步通知URL
            ip_address: IP地址
            user_agent: 用户代理
            
        Returns:
            tuple: (Payment, payment_url)，支付记录对象和支付链接
        """
        try:
            # 如果没有指定支付网关，则获取默认网关
            if not payment_gateway:
                gateway_config = PaymentGatewayConfig.get_default_gateway(order.tenant, payment_method)
                if not gateway_config:
                    raise ValueError(f"找不到支付网关配置: tenant_id={order.tenant.id}, payment_method={payment_method}")
                payment_gateway = gateway_config.gateway_type
                
                # 使用网关配置中的回调URL
                if not return_url and gateway_config.return_url:
                    return_url = gateway_config.return_url
                if not notify_url and gateway_config.notify_url:
                    notify_url = gateway_config.notify_url
            
            # 创建支付记录
            payment = Payment.objects.create(
                tenant=order.tenant,
                order=order,
                user=order.user,
                payment_method=payment_method,
                payment_gateway=payment_gateway,
                amount=order.total_amount,
                currency=order.currency,
                return_url=return_url,
                notify_url=notify_url,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # 生成支付链接
            payment_url = None
            
            if payment_method == Payment.METHOD_ALIPAY:
                # 支付宝支付
                payment_url = PaymentService.create_alipay_payment(payment, return_url, notify_url)
            elif payment_method == Payment.METHOD_WECHAT:
                # 微信支付
                payment_url = PaymentService.create_wechat_payment(payment, return_url, notify_url)
            else:
                # 其他支付方式
                raise ValueError(f"不支持的支付方式: {payment_method}")
            
            # 更新支付链接
            payment.payment_url = payment_url
            payment.save()
            
            # 更新订单支付链接
            order.payment_url = payment_url
            order.payment_method = payment_method
            order.payment_gateway = payment_gateway
            order.save()
            
            logger.info(f"支付创建成功: payment_id={payment.id}, order_id={order.id}, payment_method={payment_method}")
            return payment, payment_url
            
        except Exception as e:
            logger.error(f"创建支付失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def create_alipay_payment(payment, return_url=None, notify_url=None):
        """
        创建支付宝支付
        
        Args:
            payment: 支付记录对象
            return_url: 支付成功后跳转的URL
            notify_url: 支付结果异步通知URL
            
        Returns:
            str: 支付链接
        """
        try:
            # 如果没有指定回调URL，则使用默认URL
            if not return_url:
                return_url = settings.SITE_URL + reverse('billing_service:payment_return', args=[payment.id])
            if not notify_url:
                notify_url = settings.SITE_URL + reverse('billing_service:payment_notify', args=[payment.id])
                
            # 创建支付宝支付
            payment_url = create_alipay_trade_page_pay(payment.order, return_url, notify_url)
            
            logger.info(f"支付宝支付创建成功: payment_id={payment.id}, order_id={payment.order.id}")
            return payment_url
            
        except Exception as e:
            logger.error(f"创建支付宝支付失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def create_wechat_payment(payment, return_url=None, notify_url=None):
        """
        创建微信支付
        
        Args:
            payment: 支付记录对象
            return_url: 支付成功后跳转的URL
            notify_url: 支付结果异步通知URL
            
        Returns:
            str: 支付链接或支付参数
        """
        try:
            # 如果没有指定回调URL，则使用默认URL
            if not return_url:
                return_url = settings.SITE_URL + reverse('billing_service:payment_return', args=[payment.id])
            if not notify_url:
                notify_url = settings.SITE_URL + reverse('billing_service:payment_notify', args=[payment.id])
                
            # 创建微信支付
            payment_url = create_wechat_pay(payment.order, return_url, notify_url)
            
            logger.info(f"微信支付创建成功: payment_id={payment.id}, order_id={payment.order.id}")
            return payment_url
            
        except Exception as e:
            logger.error(f"创建微信支付失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def query_payment_status(payment):
        """
        查询支付状态
        
        Args:
            payment: 支付记录对象
            
        Returns:
            dict: 支付状态信息
        """
        try:
            if payment.payment_method == Payment.METHOD_ALIPAY:
                # 查询支付宝支付状态
                result = query_trade_status(payment.order.order_number)
                
                # 解析支付宝返回结果
                response = result.get('alipay_trade_query_response', {})
                trade_status = response.get('trade_status')
                
                if trade_status == 'TRADE_SUCCESS' or trade_status == 'TRADE_FINISHED':
                    # 支付成功
                    with transaction.atomic():
                        payment.mark_as_success(
                            transaction_id=response.get('trade_no'),
                            transaction_data=response
                        )
                    
                    return {
                        'status': 'success',
                        'message': '支付成功',
                        'data': response
                    }
                    
                elif trade_status == 'WAIT_BUYER_PAY':
                    # 等待支付
                    return {
                        'status': 'pending',
                        'message': '等待支付',
                        'data': response
                    }
                    
                else:
                    # 支付失败
                    payment.mark_as_failed(error_message=f"支付失败: {trade_status}")
                    
                    return {
                        'status': 'failed',
                        'message': f'支付失败: {trade_status}',
                        'data': response
                    }
                    
            elif payment.payment_method == Payment.METHOD_WECHAT:
                # 微信支付状态查询暂未实现
                return {
                    'status': 'not_implemented',
                    'message': '微信支付状态查询暂未实现'
                }
                
            else:
                return {
                    'status': 'error',
                    'message': f'不支持的支付方式: {payment.payment_method}'
                }
                
        except Exception as e:
            logger.error(f"查询支付状态失败: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': f'查询支付状态失败: {str(e)}'
            }
    
    @staticmethod
    def process_alipay_callback(post_data, signature=None):
        """
        处理支付宝回调
        
        Args:
            post_data: 回调POST数据
            signature: 签名
            
        Returns:
            dict: 处理结果
        """
        try:
            # 验证签名
            # 此处应该实现签名验证逻辑，暂时跳过
            
            # 解析回调数据
            if isinstance(post_data, str):
                try:
                    post_data = json.loads(post_data)
                except:
                    post_data = dict(item.split('=') for item in post_data.split('&') if item)
            
            # 获取订单号
            out_trade_no = post_data.get('out_trade_no')
            trade_no = post_data.get('trade_no')
            trade_status = post_data.get('trade_status')
            
            if not out_trade_no:
                return {
                    'status': 'error',
                    'message': '缺少订单号',
                    'success': False
                }
                
            # 查找订单
            try:
                order = Order.objects.get(order_number=out_trade_no)
            except Order.DoesNotExist:
                return {
                    'status': 'error',
                    'message': f'找不到订单: {out_trade_no}',
                    'success': False
                }
                
            # 查找支付记录
            try:
                payment = Payment.objects.filter(order=order, payment_method=Payment.METHOD_ALIPAY).latest('created_at')
            except Payment.DoesNotExist:
                return {
                    'status': 'error',
                    'message': f'找不到支付记录: {out_trade_no}',
                    'success': False
                }
                
            # 处理支付状态
            if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
                # 支付成功
                with transaction.atomic():
                    payment.mark_as_success(
                        transaction_id=trade_no,
                        transaction_data=post_data
                    )
                
                return {
                    'status': 'success',
                    'message': '支付成功',
                    'success': True
                }
                
            elif trade_status == 'WAIT_BUYER_PAY':
                # 等待支付
                return {
                    'status': 'pending',
                    'message': '等待支付',
                    'success': True
                }
                
            else:
                # 支付失败
                payment.mark_as_failed(error_message=f"支付失败: {trade_status}")
                
                return {
                    'status': 'failed',
                    'message': f'支付失败: {trade_status}',
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"处理支付宝回调失败: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': f'处理支付宝回调失败: {str(e)}',
                'success': False
            }
    
    @staticmethod
    def process_wechat_callback(post_data, signature=None):
        """
        处理微信支付回调
        
        Args:
            post_data: 回调POST数据
            signature: 签名
            
        Returns:
            dict: 处理结果
        """
        # 微信支付回调处理暂未实现
        return {
            'status': 'not_implemented',
            'message': '微信支付回调处理暂未实现',
            'success': False
        } 