def calculate_contracts(stop_distance: float,
                        risk_usd: float = 100.0,
                        usd_per_point: float = 2.0,
                        max_risk_usd: float = 130.0) -> int:
    """
    Returns the number of MNQ contracts to trade.

    Caps total risk at risk_usd ($100 target).
    Returns 0 if even 1 contract would exceed max_risk_usd ($130 hard cap).
    """
    if stop_distance <= 0:
        return 0
    risk_per_contract = stop_distance * usd_per_point
    if risk_per_contract > max_risk_usd:
        return 0
    return max(1, int(risk_usd / risk_per_contract))


def actual_risk(contracts: int, stop_distance: float, usd_per_point: float = 2.0) -> float:
    return contracts * stop_distance * usd_per_point
