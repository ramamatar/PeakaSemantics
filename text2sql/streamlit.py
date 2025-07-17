import streamlit as st
import json
import csv
import os

with open("results.json", "r", encoding="utf-8") as f:
    peaka_results= json.load(f)
with open("output.json", "r", encoding="utf-8") as f:
    spider_outputs= json.load(f)
spider_by_resultfile = {
    item.get("result-file"): item for item in spider_outputs}

st.title("Peaka AI Agent Results vs. Spider2-Snow")

databases= sorted(set(item.get("database","Unkown") for item in peaka_results))
selected_database= st.selectbox("Select Database", databases)

filtered_results=[r for r in peaka_results if r.get("database")== selected_database]

if not filtered_results:
    st.markdown("No questions found for the selected database.") 
else:
    question_titles= [f"Q{idx+1}: {r.get('question', '')[:80]}..." for idx, r in enumerate(filtered_results)]
    selected_question_idx=st.selectbox("Select Question", range(len(filtered_results)), format_func=lambda x: question_titles[x])
    selected_result=filtered_results[selected_question_idx]


    st.subheader("Peaka Result")
    st.subheader(f"Question: {selected_result.get('question', '')}")

    response_time = selected_result.get("response_time")
    if response_time is not None:
        st.markdown(f"Response Time: {response_time} seconds")
    raw_result= selected_result.get("result", "")

    try:
        parsed_result = json.loads(raw_result)
        summary= parsed_result.get("summary", "No summary available.")
        st.markdown(summary)
        data=parsed_result.get("data", [])
        if data:
            for table_idx, table in enumerate(data):
                rows=[]
                columns=[]
                for row in table:
                    if not columns:
                        columns= list(row.keys())
                    rows.append([str(row.get(col, '')) for col in columns])
                st.table(rows)
        else:
            st.markdown("No data available.")
    except json.JSONDecodeError:
        st.markdown("Error parsing result as JSON.")
        st.markdown(raw_result)


    st.subheader("Spider2-Snow Result")
    spider_match = next(
        (s for s in spider_outputs if s.get("instruction") == selected_result.get("question")),
        None
    )

    if spider_match:
        sql_query = spider_match.get("sql_query", "")
        result_file = spider_match.get("result-file")
        csv_path = os.path.join("exec_result", f"{result_file}.csv")
        if os.path.isfile(csv_path):
            with open(csv_path, "r", encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                rows = list(reader)

            if rows:
                headers = rows[0]
                data_rows = rows[1:]
                st.table([dict(zip(headers, row)) for row in data_rows])
            else:
                st.markdown("CSV file is empty.")
        else:
            st.markdown("CSV file not found for this query.")
    else:
        st.markdown("No Spider2-Snow match found for this question.")
