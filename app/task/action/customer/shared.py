async def get_logistics(order_id: str) -> dict:
    """Deprecated compatibility mock for old flow files."""
    return {
        "logistics_company": "DeprecatedMock",
        "tracking_number": order_id,
        "status": "旧版动作保留为兼容 mock，新 OpsPilot flow 不再调用。",
    }
