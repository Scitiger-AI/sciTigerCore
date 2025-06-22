"""
发票服务
实现发票相关的业务逻辑
"""

import logging
import uuid
from django.utils import timezone
from django.db import transaction

from apps.billing_service.models import Invoice, Order

logger = logging.getLogger('billing_service')


class InvoiceService:
    """
    发票服务类
    
    提供发票相关的业务逻辑
    """
    
    @staticmethod
    def generate_invoice_number():
        """
        生成发票编号
        
        Returns:
            str: 发票编号
        """
        # 格式：INV + 年月日 + 随机字符串，如：INV-20230815-a1b2c3
        now = timezone.now()
        date_str = now.strftime('%Y%m%d')
        random_str = str(uuid.uuid4()).replace('-', '')[:6]
        return f"INV-{date_str}-{random_str}"
    
    @staticmethod
    def create_invoice(tenant, user, order=None, invoice_type=Invoice.TYPE_REGULAR, amount=None, 
                       tax_amount=0, currency='CNY', title=None, tax_number=None, address=None, 
                       phone=None, bank_name=None, bank_account=None, items=None, notes=None, 
                       terms=None, created_by=None):
        """
        创建发票
        
        Args:
            tenant: 租户对象
            user: 用户对象
            order: 关联订单对象（可选）
            invoice_type: 发票类型
            amount: 发票金额（如果不指定，则使用订单金额）
            tax_amount: 税额
            currency: 货币
            title: 发票抬头
            tax_number: 税号
            address: 地址
            phone: 电话
            bank_name: 开户行
            bank_account: 银行账号
            items: 发票项目列表
            notes: 备注
            terms: 条款
            created_by: 创建者
            
        Returns:
            Invoice: 创建的发票对象
        """
        try:
            with transaction.atomic():
                # 如果关联了订单，则使用订单信息
                if order:
                    if not amount:
                        amount = order.total_amount
                    if not currency:
                        currency = order.currency
                    if not title:
                        title = f"{user.company_name if hasattr(user, 'company_name') and user.company_name else user.username}"
                        
                # 创建发票
                invoice = Invoice(
                    tenant=tenant,
                    user=user,
                    order=order,
                    invoice_number=InvoiceService.generate_invoice_number(),
                    invoice_type=invoice_type,
                    amount=amount,
                    tax_amount=tax_amount,
                    currency=currency,
                    title=title,
                    tax_number=tax_number,
                    address=address,
                    phone=phone,
                    bank_name=bank_name,
                    bank_account=bank_account,
                    items=items or [],
                    notes=notes,
                    terms=terms,
                    created_by=created_by or user
                )
                
                invoice.save()
                
                logger.info(f"创建发票: invoice_id={invoice.id}, invoice_number={invoice.invoice_number}, order_id={order.id if order else None}")
                
                return invoice
                
        except Exception as e:
            logger.error(f"创建发票失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def create_invoice_from_order(order, invoice_type=Invoice.TYPE_REGULAR, title=None, tax_number=None, 
                                  address=None, phone=None, bank_name=None, bank_account=None, 
                                  notes=None, terms=None, created_by=None):
        """
        从订单创建发票
        
        Args:
            order: 订单对象
            invoice_type: 发票类型
            title: 发票抬头
            tax_number: 税号
            address: 地址
            phone: 电话
            bank_name: 开户行
            bank_account: 银行账号
            notes: 备注
            terms: 条款
            created_by: 创建者
            
        Returns:
            Invoice: 创建的发票对象
        """
        try:
            # 检查订单状态
            if order.status != Order.STATUS_PAID:
                raise ValueError(f"只有已支付的订单才能开具发票，当前订单状态: {order.get_status_display()}")
                
            # 根据订单类型生成发票项目
            items = []
            
            if order.order_type == Order.TYPE_SUBSCRIPTION:
                # 订阅订单
                items.append({
                    'name': order.title,
                    'description': order.description or '',
                    'quantity': 1,
                    'unit_price': float(order.amount),
                    'amount': float(order.amount)
                })
            elif order.order_type == Order.TYPE_POINTS:
                # 积分订单
                items.append({
                    'name': f"积分购买",
                    'description': f"{order.points} 积分",
                    'quantity': 1,
                    'unit_price': float(order.amount),
                    'amount': float(order.amount)
                })
            else:
                # 其他订单
                items.append({
                    'name': order.title,
                    'description': order.description or '',
                    'quantity': 1,
                    'unit_price': float(order.amount),
                    'amount': float(order.amount)
                })
                
            # 添加税费
            if order.tax_amount > 0:
                items.append({
                    'name': '税费',
                    'description': '税费',
                    'quantity': 1,
                    'unit_price': float(order.tax_amount),
                    'amount': float(order.tax_amount)
                })
                
            # 添加折扣
            if order.discount_amount > 0:
                items.append({
                    'name': '折扣',
                    'description': '折扣',
                    'quantity': 1,
                    'unit_price': -float(order.discount_amount),
                    'amount': -float(order.discount_amount)
                })
                
            # 创建发票
            invoice = InvoiceService.create_invoice(
                tenant=order.tenant,
                user=order.user,
                order=order,
                invoice_type=invoice_type,
                amount=order.amount,
                tax_amount=order.tax_amount,
                currency=order.currency,
                title=title,
                tax_number=tax_number,
                address=address,
                phone=phone,
                bank_name=bank_name,
                bank_account=bank_account,
                items=items,
                notes=notes,
                terms=terms,
                created_by=created_by
            )
            
            return invoice
            
        except Exception as e:
            logger.error(f"从订单创建发票失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def issue_invoice(invoice, issue_date=None):
        """
        开具发票
        
        Args:
            invoice: 发票对象
            issue_date: 开具日期
            
        Returns:
            Invoice: 更新后的发票对象
        """
        try:
            # 开具发票
            invoice.issue(issue_date)
            
            logger.info(f"开具发票: invoice_id={invoice.id}, invoice_number={invoice.invoice_number}")
            
            return invoice
            
        except Exception as e:
            logger.error(f"开具发票失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def mark_invoice_as_paid(invoice, paid_date=None):
        """
        将发票标记为已支付
        
        Args:
            invoice: 发票对象
            paid_date: 支付日期
            
        Returns:
            Invoice: 更新后的发票对象
        """
        try:
            # 标记为已支付
            invoice.mark_as_paid(paid_date)
            
            logger.info(f"发票标记为已支付: invoice_id={invoice.id}, invoice_number={invoice.invoice_number}")
            
            return invoice
            
        except Exception as e:
            logger.error(f"标记发票为已支付失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def void_invoice(invoice, reason=None):
        """
        作废发票
        
        Args:
            invoice: 发票对象
            reason: 作废原因
            
        Returns:
            Invoice: 更新后的发票对象
        """
        try:
            # 作废发票
            invoice.void(reason)
            
            logger.info(f"作废发票: invoice_id={invoice.id}, invoice_number={invoice.invoice_number}, reason={reason}")
            
            return invoice
            
        except Exception as e:
            logger.error(f"作废发票失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def cancel_invoice(invoice, reason=None):
        """
        取消发票
        
        Args:
            invoice: 发票对象
            reason: 取消原因
            
        Returns:
            Invoice: 更新后的发票对象
        """
        try:
            # 取消发票
            invoice.cancel(reason)
            
            logger.info(f"取消发票: invoice_id={invoice.id}, invoice_number={invoice.invoice_number}, reason={reason}")
            
            return invoice
            
        except Exception as e:
            logger.error(f"取消发票失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def get_user_invoices(tenant, user, status=None, start_date=None, end_date=None):
        """
        获取用户发票
        
        Args:
            tenant: 租户对象
            user: 用户对象
            status: 发票状态
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            QuerySet: 发票查询集
        """
        try:
            # 构建查询条件
            filters = {
                'tenant': tenant,
                'user': user
            }
            
            if status:
                filters['status'] = status
                
            if start_date:
                filters['created_at__gte'] = start_date
                
            if end_date:
                filters['created_at__lte'] = end_date
                
            # 查询发票
            invoices = Invoice.objects.filter(**filters).order_by('-created_at')
            
            return invoices
            
        except Exception as e:
            logger.error(f"获取用户发票失败: {str(e)}", exc_info=True)
            raise 