#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""商城蓝图 - 提供商城相关的API接口"""
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import json

shop_bp = Blueprint('shop', __name__, url_prefix='/api/shop')

from forum.models import db, ShopCategory, ShopMerchant, ShopProduct


# ===================== 商品分类API =====================

@shop_bp.route('/categories', methods=['GET'])
@cross_origin()
def get_categories():
    """获取所有商品分类"""
    categories = ShopCategory.query.filter_by(is_active=True).order_by(ShopCategory.order_num).all()
    return jsonify({
        "success": True,
        "data": [cat.to_dict() for cat in categories],
        "total": len(categories)
    })


@shop_bp.route('/categories/<int:category_id>', methods=['GET'])
@cross_origin()
def get_category(category_id):
    """获取指定分类详情"""
    category = ShopCategory.query.get_or_404(category_id)
    return jsonify({
        "success": True,
        "data": category.to_dict()
    })


@shop_bp.route('/categories/<int:category_id>/products', methods=['GET'])
@cross_origin()
def get_category_products(category_id):
    """获取指定分类的商品列表"""
    # 验证分类是否存在
    ShopCategory.query.get_or_404(category_id)
    
    # 将category_id参数添加到请求参数中，然后调用get_products函数
    request.args = request.args.copy()
    request.args['category_id'] = category_id
    
    return get_products()


# ===================== 商家API =====================

@shop_bp.route('/merchants', methods=['GET'])
@cross_origin()
def get_merchants():
    """获取所有商家列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = ShopMerchant.query.filter_by(is_active=True)
    
    # 搜索功能
    keyword = request.args.get('keyword', '')
    if keyword:
        query = query.filter(ShopMerchant.name.contains(keyword))
    
    pagination = query.order_by(ShopMerchant.rating.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "success": True,
        "data": [m.to_dict() for m in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    })


@shop_bp.route('/merchants/<int:merchant_id>', methods=['GET'])
@cross_origin()
def get_merchant(merchant_id):
    """获取指定商家详情"""
    merchant = ShopMerchant.query.get_or_404(merchant_id)
    
    # 获取该商家的商品
    products = ShopProduct.query.filter_by(merchant_id=merchant_id, is_active=True).all()
    
    return jsonify({
        "success": True,
        "data": {
            "merchant": merchant.to_dict(),
            "products": [p.to_dict() for p in products]
        }
    })


@shop_bp.route('/merchants/<int:merchant_id>/products', methods=['GET'])
@cross_origin()
def get_merchant_products(merchant_id):
    """获取指定商家的商品列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = ShopProduct.query.filter_by(
        merchant_id=merchant_id, 
        is_active=True
    ).order_by(ShopProduct.create_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "success": True,
        "data": [p.to_dict() for p in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    })


# ===================== 商品API =====================

@shop_bp.route('/products', methods=['GET'])
@cross_origin()
def get_products():
    """获取商品列表（支持搜索和筛选）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = ShopProduct.query.filter_by(is_active=True)
    
    # 搜索功能（商品名和商家名）
    keyword = request.args.get('keyword', '')
    if keyword:
        query = query.filter(
            (ShopProduct.name.contains(keyword)) | 
            (ShopProduct.id.in_(
                db.session.query(ShopProduct.id).join(ShopMerchant).filter(ShopMerchant.name.contains(keyword))
            ))
        )
    
    # 分类筛选
    category_id = request.args.get('category_id', type=int)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # 商家筛选
    merchant_id = request.args.get('merchant_id', type=int)
    if merchant_id:
        query = query.filter_by(merchant_id=merchant_id)
    
    # 价格范围
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    if min_price is not None:
        query = query.filter(ShopProduct.price >= min_price)
    if max_price is not None:
        query = query.filter(ShopProduct.price <= max_price)
    
    # 排序
    sort_by = request.args.get('sort_by', 'create_time')
    sort_order = request.args.get('sort_order', 'desc')
    
    if sort_by == 'price':
        if sort_order == 'asc':
            query = query.order_by(ShopProduct.price.asc())
        else:
            query = query.order_by(ShopProduct.price.desc())
    elif sort_by == 'sales':
        if sort_order == 'asc':
            query = query.order_by(ShopProduct.sold_count.asc())
        else:
            query = query.order_by(ShopProduct.sold_count.desc())
    elif sort_by == 'rating':
        if sort_order == 'asc':
            query = query.order_by(ShopProduct.rating.asc())
        else:
            query = query.order_by(ShopProduct.rating.desc())
    else:
        if sort_order == 'asc':
            query = query.order_by(ShopProduct.create_time.asc())
        else:
            query = query.order_by(ShopProduct.create_time.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "success": True,
        "data": [p.to_dict() for p in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    })


@shop_bp.route('/products/<int:product_id>', methods=['GET'])
@cross_origin()
def get_product(product_id):
    """获取商品详情"""
    product = ShopProduct.query.get_or_404(product_id)
    
    # 增加浏览量
    product.view_count += 1
    db.session.commit()
    
    return jsonify({
        "success": True,
        "data": product.to_dict()
    })


@shop_bp.route('/products/featured', methods=['GET'])
@cross_origin()
def get_featured_products():
    """获取推荐商品"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = ShopProduct.query.filter_by(
        is_active=True, 
        is_featured=True
    ).order_by(ShopProduct.create_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "success": True,
        "data": [p.to_dict() for p in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    })


@shop_bp.route('/products/search', methods=['GET'])
@cross_origin()
def search_products():
    """搜索商品（支持商品名和商家名）"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({
            "success": False,
            "message": "请提供搜索关键词"
        }), 400
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 搜索商品名称
    products_query = ShopProduct.query.filter(
        ShopProduct.is_active == True,
        ShopProduct.name.contains(keyword)
    )
    
    # 同时搜索商家名称匹配的商家ID
    merchants = ShopMerchant.query.filter(
        ShopMerchant.is_active == True,
        ShopMerchant.name.contains(keyword)
    ).all()
    
    merchant_ids = [m.id for m in merchants]
    
    if merchant_ids:
        products_query = products_query.union(
            ShopProduct.query.filter(
                ShopProduct.is_active == True,
                ShopProduct.merchant_id.in_(merchant_ids)
            )
        )
    
    # 获取总数（去重后）
    total = products_query.count()
    
    # 分页
    products = products_query.order_by(ShopProduct.create_time.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    return jsonify({
        "success": True,
        "data": [p.to_dict() for p in products],
        "total": total,
        "page": page,
        "per_page": per_page,
        "keyword": keyword
    })


# ===================== 商城首页数据API =====================

@shop_bp.route('/home', methods=['GET'])
@cross_origin()
def get_shop_home():
    """获取商城首页数据"""
    # 获取分类
    categories = ShopCategory.query.filter_by(is_active=True).order_by(ShopCategory.order_num).limit(10).all()
    
    # 获取推荐商品
    featured_products = ShopProduct.query.filter_by(
        is_active=True, 
        is_featured=True
    ).order_by(ShopProduct.create_time.desc()).limit(10).all()
    
    # 获取热门商家
    top_merchants = ShopMerchant.query.filter_by(is_active=True).order_by(
        ShopMerchant.rating.desc(), 
        ShopMerchant.total_sales.desc()
    ).limit(10).all()
    
    # 获取最新商品
    latest_products = ShopProduct.query.filter_by(is_active=True).order_by(
        ShopProduct.create_time.desc()
    ).limit(20).all()
    
    return jsonify({
        "success": True,
        "data": {
            "categories": [cat.to_dict() for cat in categories],
            "featured_products": [p.to_dict() for p in featured_products],
            "top_merchants": [m.to_dict() for m in top_merchants],
            "latest_products": [p.to_dict() for p in latest_products]
        }
    })


# ===================== 统计数据API =====================

@shop_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_stats():
    """获取商城统计数据"""
    return jsonify({
        "success": True,
        "data": {
            "category_count": ShopCategory.query.filter_by(is_active=True).count(),
            "merchant_count": ShopMerchant.query.filter_by(is_active=True).count(),
            "product_count": ShopProduct.query.filter_by(is_active=True).count()
        }
    })
