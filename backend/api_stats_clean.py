

# ===================== 数据统计模块 API =====================

@app.get("/api/stats/daily-stats")
def get_stats_daily(
    mode: str = Query("daily"),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """数据日统计 / 按月统计"""
    fmt = "%Y-%m-%d" if mode == "daily" else "%Y-%m"
    now = datetime.now()
    if mode == "daily":
        start = now - timedelta(days=90)
        date_col = func.date(Customer.created_at)
    else:
        start = now - timedelta(days=365)
        date_col = func.strftime("%Y-%m", Customer.created_at)

    rows = db.query(
        date_col.label("date"),
        func.count(Customer.id).label("new_apply_count"),
    ).filter(Customer.created_at >= start).group_by(date_col).all()

    result = []
    for r in rows:
        date_str = r.date
        customers = db.query(Customer).filter(
            func.date(Customer.created_at) == date_str if mode == "daily" else func.strftime("%Y-%m", Customer.created_at) == date_str
        ).all()
        entry = {"date": str(date_str), "new_apply_count": r.new_apply_count,
                 "new_accepted": 0, "new_pending": 0,
                 "new_star0": 0, "new_star1": 0, "new_star2": 0,
                 "new_star3": 0, "new_star4": 0, "new_star5": 0, "new_spam": 0,
                 "reassign_count": 0, "re_accepted": 0, "re_pending": 0,
                 "re_star1": 0, "re_star2": 0, "re_star3": 0, "re_star4": 0, "re_star5": 0, "re_spam": 0}
        for c in customers:
            s = c.star_level or 0
            if 0 <= s <= 5:
                entry["new_star" + str(s)] += 1
            if c.status == 1: entry["new_accepted"] += 1
            if c.status == 3: entry["new_pending"] += 1
            if c.status == 99: entry["new_spam"] += 1
        re_assignments = db.query(CustomerAssignment).filter(
            CustomerAssignment.pool_type == 2,
            func.date(CustomerAssignment.assigned_at) == date_str if mode == "daily" else func.strftime("%Y-%m", CustomerAssignment.assigned_at) == date_str
        ).all()
        entry["reassign_count"] = len(re_assignments)
        for a in re_assignments:
            c = db.query(Customer).filter(Customer.id == a.customer_id).first()
            if c:
                s = c.star_level or 0
                if 1 <= s <= 5: entry["re_star" + str(s)] += 1
                if c.status == 1: entry["re_accepted"] += 1
                if c.status == 3: entry["re_pending"] += 1
                if c.status == 99: entry["re_spam"] += 1
        total_new = entry["new_star3"] + entry["new_star4"] + entry["new_star5"]
        denom = max(entry["new_apply_count"], 1)
        entry["new_lendable_rate"] = round(total_new / denom * 100, 1)
        entry["new_star3plus_rate"] = round(total_new / denom * 100, 1)
        result.append(entry)
    return sorted(result, key=lambda x: x["date"], reverse=True)


@app.get("/api/stats/remark-counts")
def get_stats_remark_counts(
    mode: str = Query("daily"),
    user: User = Depends(get_current_user), db: Session = Depends(get_db")
):
    """备注数量日统计"""
    if mode == "daily":
        start = datetime.now() - timedelta(days=90)
        date_col = func.date(CustomerRemark.created_at)
    else:
        start = datetime.now() - timedelta(days=365)
        date_col = func.strftime("%Y-%m", CustomerRemark.created_at)

    rows = db.query(
        date_col.label("date"),
        func.count(CustomerRemark.id).label("total_remarks"),
        func.count(func.distinct(CustomerRemark.customer_id)).label("customers_with_remark")
    ).filter(CustomerRemark.created_at >= start).group_by(date_col).all()

    result = []
    for r in rows:
        total = r.total_remarks or 0
        cw = r.customers_with_remark or 0
        result.append({
            "date": str(r.date),
            "total_remarks": total,
            "customers_with_remark": cw,
            "avg_remarks": round(total / max(cw, 1), 1),
            "customers_no_remark": 0
        })
    return sorted(result, key=lambda x: x["date"], reverse=True)


@app.get("/api/stats/my-remarks")
def get_stats_my_remarks(
    page: int = Query(1), page_size: int = Query(20),
    user: User = Depends(get_current_user), db: Session = Depends(get_db")
):
    """我的备注记录"""
    q = db.query(CustomerRemark).filter(CustomerRemark.advisor_id == user.id)
    total = q.count()
    remarks = q.order_by(CustomerRemark.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for r in remarks:
        c = db.query(Customer).filter(Customer.id == r.customer_id).first()
        items.append({
            "id": r.id,
            "customer_id": r.customer_id,
            "customer_name": c.name if c else "",
            "content": r.content,
            "star_before": r.star_before,
            "star_after": r.star_after,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else ""
        })
    return {"total": total, "items": items}


@app.get("/api/stats/upcoming-pool")
def get_stats_upcoming_pool(
    user: User = Depends(get_current_user), db: Session = Depends(get_db")
):
    """即将抓入公共池（超过N天未备注的客户）"""
    cutoff = datetime.now() - timedelta(days=15)
    if user.role >= 2:
        customers = db.query(Customer).filter(
            or_(Customer.last_remark_at == None, Customer.last_remark_at < cutoff)
        ).all()
    else:
        cust_ids = [a.customer_id for a in db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id == user.id,
            CustomerAssignment.status == 1
        ).all()]
        customers = db.query(Customer).filter(
            Customer.id.in_(cust_ids),
            or_(Customer.last_remark_at == None, Customer.last_remark_at < cutoff)
        ).all()
    result = []
    for c in customers:
        days = (datetime.now() - (c.last_remark_at or c.created_at)).days
        advisor_name = ""
        asgn = db.query(CustomerAssignment).filter(
            CustomerAssignment.customer_id == c.id, CustomerAssignment.status == 1
        ).first()
        if asgn:
            u = db.query(User).filter(User.id == asgn.advisor_id).first()
            if u: advisor_name = u.real_name
        result.append({
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "advisor_name": advisor_name,
            "last_remark_at": c.last_remark_at.strftime("%Y-%m-%d %H:%M") if c.last_remark_at else "从未备注",
            "no_remark_days": days
        })
    return {"items": result}


@app.get("/api/stats/new-customer-stats")
def get_stats_new_customer(
    user: User = Depends(get_current_user), db: Session = Depends(get_db")
):
    """顾问新数据统计（管理员视角）"""
    if user.role < 2:
        return {"items": []}
    users = db.query(User).filter(User.role == 1, User.dept_id == user.dept_id).all()
    result = []
    for u in users:
        assignments = db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id == u.id,
            CustomerAssignment.pool_type == 1,
            CustomerAssignment.assigned_at >= datetime.now() - timedelta(days=30)
        ).all()
        new_count = len(assignments)
        contacted = 0
        star3plus = 0
        for a in assignments:
            c = db.query(Customer).filter(Customer.id == a.customer_id).first()
            if c:
                if c.last_remark_at: contacted += 1
                if (c.star_level or 0) >= 3: star3plus += 1
        result.append({
            "advisor_name": u.real_name,
            "new_count": new_count,
            "contacted_count": contacted,
            "contact_rate": round(contacted / max(new_count, 1) * 100, 1),
            "star3plus_count": star3plus,
            "high_intent_rate": round(star3plus / max(new_count, 1) * 100, 1)
        })
    return {"items": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
