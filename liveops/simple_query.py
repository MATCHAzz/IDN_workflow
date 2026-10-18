"""The single active fixed business-query example: total successful gifts in a period."""
from . import validation

SQL="""SELECT COALESCE(SUM(amount_idr),0) AS gift_amount_idr
FROM transactions WHERE date BETWEEN :start_date AND :end_date"""


def query_gift_total(store,meta,start_date,end_date):
    validation.require_quality(store,start_date,end_date,meta)
    rows=store.query("simple_fixed_gift_total",SQL,{"start_date":start_date,"end_date":end_date})
    return {"title":"固定查询：打赏金额","date_range":[start_date,end_date],"rows":rows,"unit":"IDR",
            "mode":"fixed_python_query","note":"保留的最简单固定业务查询；其它业务分析走Agent生成SQL。"}


def main():
    import argparse,json
    from .tools import ToolRegistry
    parser=argparse.ArgumentParser(description="指定日期范围的打赏金额固定查询")
    parser.add_argument("--start-date",required=True)
    parser.add_argument("--end-date",required=True)
    parser.add_argument("--run-id")
    args=parser.parse_args()
    response=ToolRegistry().call("query_gift_total",{"start_date":args.start_date,"end_date":args.end_date},args.run_id)
    print(json.dumps({k:v for k,v in response.items() if k!="queries"},ensure_ascii=False,indent=2))
    return 0 if response["status"]=="ok" else 1


if __name__=="__main__":
    raise SystemExit(main())
