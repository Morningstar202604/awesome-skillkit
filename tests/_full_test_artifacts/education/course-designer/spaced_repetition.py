
def next_review(day, last_rating="good"):
    # 简化 Ebbinghaus：基础间隔 [1,2,4,7,14,30]，按记忆轮次递增
    base = [1, 2, 4, 7, 14, 30, 60]
    if day < 0:
        raise ValueError("day must be >= 0")
    if last_rating == "bad":
        idx = 0
    elif last_rating == "easy":
        idx = min(day + 2, len(base) - 1)
    else:
        idx = min(day + 1, len(base) - 1)
    return base[idx]

if __name__ == "__main__":
    seq = [next_review(i, "good") for i in range(6)]
    print("intervals:", seq)
    assert seq == sorted(seq), "intervals must be non-decreasing"
    print("monotonic OK", seq)
