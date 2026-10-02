def calculate_risk_score(speaker_verified, similarity_score, spoof_probability):
    """
    Risk score:
    0   = Low risk
    100 = Critical risk
    """

    speaker_risk = max(0.0, 1.0 - similarity_score) * 40
    deepfake_risk = spoof_probability * 60

    risk_score = speaker_risk + deepfake_risk
    risk_score = round(min(max(risk_score, 0), 100), 2)

    if risk_score < 25:
        risk_level = "Low"
    elif risk_score < 50:
        risk_level = "Medium"
    elif risk_score < 75:
        risk_level = "High"
    else:
        risk_level = "Critical"

    if not speaker_verified:
        risk_score = max(risk_score, 60)

        if risk_score < 75:
            risk_level = "High"
        else:
            risk_level = "Critical"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level
    }