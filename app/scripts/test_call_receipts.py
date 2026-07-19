from app.services.call_receipt_service import fetch_call_receipts_raw

if __name__ == "__main__":
    r = fetch_call_receipts_raw(page=1, size=5, sort="dclrDt,desc") 
    print("전체 건수:", r["total"])
    print("최신순 샘플:", [(i.get("cntrNm"), i.get("dclrYmd"), i.get("sittnEndDt")) for i in r["items"]])