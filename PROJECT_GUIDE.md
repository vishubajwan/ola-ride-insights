# Evaluation & Presentation Guide (from your GUVI documents)

## 30-minute live evaluation
| Part | Time | What to do |
|---|---|---|
| Self introduction | 3 min | Name, background, skills (SQL, Python, Power BI, Streamlit) |
| Problem statement + project explanation | 12 min | Use the 10-point script below + live demo of dashboard and app |
| Mock questions (1-2 per technology) | 10 min | Q&A bank below |
| Feedback | 5 min | |

## Marks (60) and how this project covers each
| Metric | Marks | Where it is covered |
|---|---|---|
| Code quality / data transformations | 10 | `clean_data.py` (commented, step by step) |
| Documentation (GitHub README / insights / PPT) | 10 | `README.md`, insights section, short PPT |
| Code reusability / DAX standard | 10 | Modular scripts, `queries.sql` loaded by app, DAX measures in `powerbi_guide.md` (use measures, not calculated columns) |
| Presentation | 10 | Script below, keep every point to 1-2 lines |
| Task accomplishment | 10 | All 4 deliverables: SQL, Power BI, Streamlit, insights |
| 5 mock questions | 10 | Q&A bank below |

## Capstone explanation script (numbers already filled from your data) (Analysis project: 1-2 lines each)
Fill the numbers from your real results.
1. **Domain (3 lines):** Ride-sharing has changed urban mobility. Platforms like Ola produce huge booking data. Analysing it improves operations and customer experience.
2. **Project (2 lines):** Analysis of Ola ride bookings using SQL, Power BI and Streamlit to find demand, cancellation, revenue and rating patterns.
3. **Objective (2 lines):** Turn raw booking data into decisions: peak-hour driver allocation, fewer cancellations, better revenue and satisfaction.
4. **ELT approach:** Loaded raw CSV first, then transformed with Python (pandas) and stored in SQL (`ola.db`/MySQL) for querying.
5. **Data migration:** Skip or say "CSV to SQL database via pandas `to_sql`" (no MongoDB used).
6. **EDA findings:** Success rate 62.1%, drivers cancel 17.9% vs customers 10.2%, Cash 54.8% / UPI 40.5%, top customer cancel reason "driver not moving towards pickup" (30.2%), demand is flat across hours/days.
7. **Feature engineering:** `booking_datetime`, `hour`, `day_of_week`, `time_slot`, `is_success`.
8. **Statistical technique:** Chi-square to test if booking status depends on vehicle type (both categorical); Spearman for distance vs value (non-normal data).
9. **Conclusion:** 2-3 key findings.
10. **Business suggestions:** More drivers at peak slots; fix address/pickup issues behind customer cancellations; driver incentives; target low-rated vehicle types.

## Likely mock questions
- **SQL:** WHERE vs HAVING? INNER vs LEFT JOIN? GROUP BY use? How do you find the top 5 customers? What is a window function (`RANK() OVER`)?
- **Power BI:** Calculated column vs measure? What is DAX `CALCULATE`? What is a slicer? Import vs DirectQuery? How did you connect MySQL?
- **Python/Streamlit:** How did you handle nulls (and why not impute)? What does `@st.cache_data` do? How did you embed Power BI?
- **EDA:** How do you detect outliers (IQR / Z-score)? Why median for skewed data? What did you find?
- **Project:** Why are ratings null for cancelled rides? What would you do with more data (demand forecasting, surge pricing, fraud detection)?

## Free Power BI work account (summary of your PDF)
Sign in at microsoft.com with your personal account → search "Office 365 E5" → Free trial → enter email → fill details → choose an `xxx.onmicrosoft.com` business name → create user ID + password (save it!) → Sign up → verify via email → Power BI Desktop → Sign in with the new work account → Publish.
