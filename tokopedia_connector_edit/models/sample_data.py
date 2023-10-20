get_token = {
  "access_token": "c:knbKn0uaQES4zCIU8m0gCw",
  "event_code": "",
  "expires_in": 76201,
  "last_login_type": "8",
  "sq_check": False,
  "token_type": "Bearer"
}

get_whitelist = {
  "header": {
    "process_time": 0,
    "messages": "Your request has been processed successfully"
  },
  "data": {
    "fs_id": 17546,
    "ip_whitelisted": [
      "172.17.0.1",
      "172.26.0.1",
      "18.139.9.214",
      "194.233.84.213"
    ]
  }
}

get_shop = {
  "header": {
    "process_time": 22,
    "messages": "Successfully get retrieved shop info data",
    "reason": "",
    "error_code": 0
  },
  "data": [
    {
      "shop_id": 14952824,
      "user_id": 223449164,
      "shop_name": "SellerAPI-Odoo Tokped",
      "logo": "https://images.tokopedia.net/img/seller_no_logo_0.png",
      "shop_url": "https://www.tokopedia.com/sellerapi-odootokped",
      "is_open": 1,
      "status": 1,
      "date_shop_created": "2022-12-18",
      "domain": "sellerapi-odootokped",
      "admin_id": [
        223449164
      ],
      "reason": "",
      "district_id": 1,
      "province_name": "D.I. Aceh",
      "warehouses": [
        {
          "warehouse_id": 14811979,
          "partner_id": {
            "Int64": 0,
            "Valid": False
          },
          "shop_id": {
            "Int64": 14952824,
            "Valid": True
          },
          "warehouse_name": "Shop Location",
          "district_id": 1,
          "district_name": "Kaway XVI",
          "city_id": 1,
          "city_name": "Kab. Aceh Barat",
          "province_id": 1,
          "province_name": "D.I. Aceh",
          "status": 1,
          "postal_code": "23681",
          "is_default": 1,
          "latlon": ",",
          "latitude": "",
          "longitude": "",
          "email": "",
          "address_detail": "",
          "phone": "",
          "wh_type": "Default Shop Location"
        }
      ],
      "subscribe_tokocabang": False,
      "is_mitra": False
    }
  ]
}

get_all_order = {
    "header": {
        "process_time": 0.018328845,
        "messages": "Your request has been processed successfully"
    },
    "data": [
        {
            "fs_id": "13004",
            "order_id": 43481289,
            "is_cod_mitra": False,
            "accept_partial": False,
            "invoice_ref_num": "INV/20200110/XX/I/502",
            "have_product_bundle": True,
            "products": [
                {
                    "id": 2147967676,
                    "Name": "[DEV] TEST BARANG",
                    "quantity": 4,
                    "notes": "",
                    "weight": 0.1,
                    "total_weight": 0.4,
                    "price": 10000,
                    "total_price": 40000,
                    "currency": "Rp",
                    "sku": "",
                    "is_wholesale": False
                },
                {
                    "id": 2147967676,
                    "Name": "[DEV] TEST BARANG",
                    "quantity": 1,
                    "notes": "",
                    "weight": 0.1,
                    "total_weight": 0.1,
                    "price": 100000,
                    "total_price": 100000,
                    "currency": "Rp",
                    "sku": "",
                    "is_wholesale": False
                }
            ],
            "products_fulfilled": [
                {
                    "product_id": 2147967676,
                    "quantity_deliver": 4,
                    "quantity_reject": 0
                },
                {
                    "product_id": 2147967676,
                    "quantity_deliver": 1,
                    "quantity_reject": 0
                }
            ],
            "bundle_detail": {
                "bundle": [
                    {
                        "bundle_id": 8925,
                        "bundle_variant_id": "bid:8925-pid:2147967676-pid1:2147967676",
                        "bundle_name": "Paket Murah",
                        "bundle_price": 40000,
                        "bundle_quantity": 1,
                        "bundle_subtotal_price": 40000,
                        "order_detail": [
                            {
                                "order_dtl_id": 20627504,
                                "order_id": 167046488,
                                "product_id": 2147967676,
                                "product_name": "[DEV] TEST BARANG",
                                "product_desc": "",
                                "quantity": 4,
                                "product_price": 10000,
                                "product_weight": 0.1,
                                "total_weight": 0.4,
                                "subtotal_price": 40000,
                                "notes": "",
                                "finsurance": 1,
                                "returnable": 0,
                                "child_cat_id": 0,
                                "currency_id": 1,
                                "insurance_price": 0,
                                "normal_price": 100000,
                                "currency_rate": 1,
                                "prod_pic": "[{\"file_name\":\"cf50e595-6d09-43b6-8043-1a75df4d2910.jpg\",\"file_path\":\"hDjmkQ/2021/11/12\",\"status\":2}]",
                                "min_order": 4,
                                "must_insurance": 0,
                                "condition": 1,
                                "campaign_id": 0,
                                "sku": "",
                                "is_slash_price": False,
                                "oms_detail_data": "",
                                "thumbnail": "https://ecs7.tokopedia.net/img/cache/100-square/hDjmkQ/2021/11/12/cf50e595-6d09-43b6-8043-1a75df4d2910.jpg",
                                "bundle_id": 8925,
                                "bundle_variant_id": "bid:8925-pid:2147967676-pid1:2147967676"
                            }
                        ]
                    }
                ],
                "non_bundle": [
                    {
                        "order_dtl_id": 20627505,
                        "order_id": 167046488,
                        "product_id": 2147967676,
                        "product_name": "[DEV] TEST BARANG",
                        "product_desc": "",
                        "quantity": 1,
                        "product_price": 100000,
                        "product_weight": 0.1,
                        "total_weight": 0.1,
                        "subtotal_price": 100000,
                        "notes": "",
                        "finsurance": 1,
                        "returnable": 0,
                        "child_cat_id": 0,
                        "currency_id": 1,
                        "insurance_price": 0,
                        "normal_price": 100000,
                        "currency_rate": 1,
                        "prod_pic": "[{\"file_name\":\"cf50e595-6d09-43b6-8043-1a75df4d2910.jpg\",\"file_path\":\"hDjmkQ/2021/11/12\",\"status\":2}]",
                        "min_order": 0,
                        "must_insurance": 0,
                        "condition": 1,
                        "campaign_id": 0,
                        "sku": "",
                        "is_slash_price": False,
                        "oms_detail_data": "",
                        "thumbnail": "https://ecs7.tokopedia.net/img/cache/100-square/hDjmkQ/2021/11/12/cf50e595-6d09-43b6-8043-1a75df4d2910.jpg"
                    }
                ],
                "total_product": 1
            },
            "device_type": "",
            "buyer": {
                "id": 8970588,
                "Name": "Mitra Test Account",
                "phone": "*******8888",
                "email": " "
            },
            "shop_id": 479066,
            "payment_id": 11687315,
            "recipient": {
                "Name": "Mitra Test Account",
                "phone": "62888888888",
                "address": {
                    "address_full": "Kobakma, Kab. Mamberamo Tengah, Papua, 99558",
                    "district": "Kobakma",
                    "city": "Kab. Mamberamo Tengah",
                    "province": "Papua",
                    "country": "Indonesia",
                    "postal_code": "99558",
                    "district_id": 5455,
                    "city_id": 555,
                    "province_id": 33,
                    "geo": "-3.69624360109313,139.10973580486393"
                }
            },
            "logistics": {
                "shipping_id": 999,
                "district_id": 0,
                "city_id": 0,
                "province_id": 0,
                "geo": "",
                "shipping_agency": "Custom Logistik",
                "service_type": "Service Normal"
            },
            "amt": {
                "ttl_product_price": 98784,
                "shipping_cost": 10000,
                "insurance_cost": 0,
                "ttl_amount": 108784,
                "voucher_amount": 0,
                "toppoints_amount": 0
            },
            "dropshipper_info": {},
            "voucher_info": {
                "voucher_code": "",
                "voucher_type": 0
            },
            "order_status": 700,
            "warehouse_id": 0,
            "fulfill_by": 0,
            "create_time": 1578671153,
            "custom_fields": {
                "awb": "CSDRRRRR502"
            },
            "promo_order_detail": {
                "order_id": 43481289,
                "total_cashback": 0,
                "total_discount": 20000,
                "total_discount_product": 10000,
                "total_discount_shipping": 10000,
                "total_discount_details":[
                    {
                      "amount":10000,
                      "Type":"discount_product"
                    },
                    {
                      "amount":10000,
                      "Type":"discount_shipping"
                    }
                ],
                "summary_promo": [
                    {
                        "Name": "Promo Product July",
                        "is_coupon": False,
                        "show_cashback_amount": True,
                        "show_discount_amount": True,
                        "cashback_amount": 0,
                        "cashback_points": 0,
                        "Type": "discount",
                        "discount_amount": 10000,
                        "discount_details": [
                          {
                             "amount" : 10000,
                             "Type"   : "discount_product"
                          }
                         ],
                        "invoice_desc": "PRODUCTDISC"
                    },
                    {
                        "Name": "Promo Ongkir",
                        "is_coupon": False,
                        "show_cashback_amount": True,
                        "show_discount_amount": True,
                        "cashback_amount": 0,
                        "cashback_points": 0,
                        "Type": "discount",
                        "discount_amount": 10000,
                        "discount_details": [
                           {
                             "amount" : 10000,
                             "Type"   : "discount_shipping"
                           }
                         ],
                        "invoice_desc": "ONGKIRFREE"
                    }
                ]
            }
        }
    ]
}

get_single_order = {
    "header": {
        "process_time": 0.149503274,
        "messages": "Your request has been processed successfully"
    },
    "data": 
                {
                    "order_id": 12472302,
                    "buyer_id": 5511917,
                    "seller_id": 479573,
                    "payment_id": 11539459,
                    "is_affiliate": False,
                    "is_fulfillment": False,
                    "order_warehouse": {
                        "warehouse_id": 0,
                        "fulfill_by": 0,
                        "meta_data": {
                            "warehouse_id": 0,
                            "partner_id": 0,
                            "shop_id": 0,
                            "warehouse_name": "",
                            "district_id": 0,
                            "district_name": "",
                            "city_id": 0,
                            "city_name": "",
                            "province_id": 0,
                            "province_name": "",
                            "status": 0,
                            "postal_code": "",
                            "is_default": 0,
                            "latlon": "",
                            "latitude": "",
                            "longitude": "",
                            "email": "",
                            "address_detail": "",
                            "country_name": "",
                            "is_fulfillment": False
                        }
                    },
                    "order_status": 0,
                    "invoice_number": "INV/20170720/XVII/VII/12472252",
                    "invoice_pdf": "Invoice-5511917-479573-20170720175058-WE1NWElRVVk.pdf",
                    "invoice_url": "https://staging.tokopedia.com/invoice.pl?id=12472302&pdf=Invoice-5511917-479573-20170720175058-WE1NWElRVVk",
                    "open_amt": 270000,
                    "lp_amt": 0,
                    "cashback_amt": 0,
                    "info": "",
                    "comment": "* 24/07/2017 08:01:07 : Penjual telah melebihi batas waktu proses pesanan",
                    "item_price": 261000,
                    "buyer_info": {
                        "buyer_id": 5511917,
                        "buyer_fullname": "Maulana Hasim",
                        "buyer_email": " ",
                        "buyer_phone": "*******0644"
                    },
                    "shop_info": {
                        "shop_owner_id": 5510391,
                        "shop_owner_email": "hana.mahrifah+inti@tokopedia.com",
                        "shop_owner_phone": "628119916444",
                        "shop_name": "I`nti.Cosmetic",
                        "shop_domain": "icl",
                        "shop_id": 479573
                    },
                    "shipment_fulfillment": {
                        "id": 0,
                        "order_id": 0,
                        "payment_date_time": "0001-01-01T00:00:00Z",
                        "is_same_day": False,
                        "accept_deadline": "0001-01-01T00:00:00Z",
                        "confirm_shipping_deadline": "0001-01-01T00:00:00Z",
                        "item_delivered_deadline": {
                            "Time": "0001-01-01T00:00:00Z",
                            "Valid": False
                        },
                        "is_accepted": False,
                        "is_confirm_shipping": False,
                        "is_item_delivered": False,
                        "fulfillment_status": 0
                    },
                    "preorder": {
                        "order_id": 0,
                        "preorder_type": 0,
                        "preorder_process_time": 0,
                        "preorder_process_start": "2017-07-20T17:50:58.061156Z",
                        "preorder_deadline": "0001-01-01T00:00:00Z",
                        "shop_id": 0,
                        "customer_id": 0
                    },
                    "order_info": {
                        "order_detail": [
                            {
                                "order_detail_id": 20274955,
                                "product_id": 14286600,
                                "product_name": "STABILO Paket Ballpoint Premium Bionic Rollerball - Multicolor",
                                "product_desc_pdp": "Paket\n pulpen premium membuat kegiatan menulis kamu bisa lebih berwarna kenyamanan yang maksimal- memiliki 4 warna Paket\n pulpen premium membuat kegiatan menulis kamu bisa lebih berwarna kenyamanan yang maksimal- memiliki 4 warna",
                                "product_desc_atc": "Paket\n pulpen premium membuat kegiatan menulis kamu bisa lebih berwarna kenyamanan yang maksimal- memiliki 4 warna Paket\n pulpen premium membuat kegiatan menulis kamu bisa lebih berwarna kenyamanan yang maksimal- memiliki 4 warna",
                                "product_price": 261000,
                                "subtotal_price": 261000,
                                "weight": 0.2,
                                "total_weight": 0.2,
                                "quantity": 1,
                                "quantity_deliver": 1,
                                "quantity_reject": 0,
                                "is_free_returns": False,
                                "insurance_price": 0,
                                "normal_price": 0,
                                "currency_id": 2,
                                "currency_rate": 0,
                                "min_order": 0,
                                "child_cat_id": 1122,
                                "campaign_id": "",
                                "product_picture": "https://imagerouter-staging.tokopedia.com/image/v1/p/14286600/product_detail/desktop",
                                "snapshot_url": "https://staging.tokopedia.com/snapshot_product?order_id=12472302&dtl_id=20274955",
                                "sku": "SKU01"
                            }
                        ],
                        "order_history": [
                            {
                                "action_by": "system-automatic",
                                "hist_status_code": 0,
                                "message": "",
                                "timestamp": "2017-07-24T08:01:07.073696Z",
                                "comment": "Penjual telah melebihi batas waktu proses pesanan",
                                "create_by": 0,
                                "update_by": "system"
                            },
                            {
                                "action_by": "buyer",
                                "hist_status_code": 220,
                                "message": "",
                                "timestamp": "2017-07-20T17:50:58.374626Z",
                                "comment": "",
                                "create_by": 0,
                                "update_by": "tokopedia"
                            },
                            {
                                "action_by": "buyer",
                                "hist_status_code": 100,
                                "message": "",
                                "timestamp": "2017-07-20T17:50:58.374626Z",
                                "comment": "",
                                "create_by": 0,
                                "update_by": "system"
                            }
                        ],
                        "order_age_day": 812,
                        "shipping_age_day": 0,
                        "delivered_age_day": 0,
                        "partial_process": False,
                        "shipping_info": {
                            "sp_id": 1,
                            "shipping_id": 1,
                            "logistic_name": "Kurir Rekomendasi",
                            "logistic_service": "Reguler",
                            "shipping_price": 9000,
                            "shipping_price_rate": 9000,
                            "shipping_fee": 0,
                            "insurance_price": 0,
                            "fee": 0,
                            "is_change_courier": False,
                            "second_sp_id": 0,
                            "second_shipping_id": 0,
                            "second_logistic_name": "",
                            "second_logistic_service": "",
                            "second_agency_fee": 0,
                            "second_insurance": 0,
                            "second_rate": 0,
                            "awb": "",
                            "autoresi_cashless_status": 0,
                            "autoresi_awb": "",
                            "autoresi_shipping_price": 0,
                            "count_awb": 0,
                            "isCashless": False,
                            "is_fake_delivery": False,
                            "recommended_courier_info": [
                            {
                                "name": "SICEPAT",
                                "sequence": 1,
                                "milestone": "first_mile"
                            },
                            {
                                "name": "JNE",
                                "sequence": 2,
                                "milestone": "last_mile"
                            }
                            ]
                        },
                        "destination": {
                            "receiver_name": "maul",
                            "receiver_phone": "085712345678",
                            "address_street": "jalan gatot subroto kav 123456789",
                            "address_district": "Jagakarsa",
                            "address_city": "Kota Administrasi Jakarta Selatan",
                            "address_province": "DKI Jakarta",
                            "address_postal": "123456",
                            "customer_address_id": 4649619,
                            "district_id": 2263,
                            "city_id": 175,
                            "province_id": 13
                        },
                        "is_replacement": False,
                        "replacement_multiplier": 0
                    },
                    "origin_info": {
                        "sender_name": "I`nti.Cosmetic",
                        "origin_province": 13,
                        "origin_province_name": "DKI Jakarta",
                        "origin_city": 174,
                        "origin_city_name": "Kota Administrasi Jakarta Barat",
                        "origin_address": "Jalan Letjen S. Parman, Palmerah, 11410",
                        "origin_district": 2258,
                        "origin_district_name": "Palmerah",
                        "origin_postal_code": "",
                        "origin_geo": "-6.190449999999999,106.79771419999997",
                        "receiver_name": "maul",
                        "destination_address": "jalan gatot subroto kav 123456789",
                        "destination_province": 13,
                        "destination_city": 175,
                        "destination_district": 2263,
                        "destination_postal_code": "123456",
                        "destination_geo": ",",
                        "destination_loc": {
                            "lat": 0,
                            "lon": 0
                        }
                    },
                    "payment_info": {
                        "payment_id": 11539459,
                        "payment_ref_num": "PYM/20170720/XVII/VII/4999664",
                        "payment_date": "2017-07-20T17:50:06Z",
                        "payment_method": 0,
                        "payment_status": "Verified",
                        "payment_status_id": 2,
                        "create_time": "2017-07-20T17:50:06Z",
                        "pg_id": 12,
                        "gateway_name": "Installment Payment",
                        "discount_amount": 0,
                        "voucher_code": "",
                        "voucher_id": 0
                    },
                    "insurance_info": {
                        "insurance_type": 0
                    },
                    "hold_info": False,
                    "cancel_request_info": False,
                    "create_time": "2017-07-20T17:50:58.061156Z",
                    "shipping_date": False,
                    "update_time": "2017-07-24T08:01:07.073696Z",
                    "payment_date": "2017-07-20T17:50:58.061156Z",
                    "delivered_date": False,
                    "est_shipping_date": False,
                    "est_delivery_date": False,
                    "related_invoices": False,
                    "custom_fields": False
                }
}
